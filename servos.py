import asyncio
import logging
from typing import Any, Dict, List
import time
from datetime import timedelta

from hparams import HPARAMS, Servo, Pose, Move
from utils import async_task

from dynamixel_sdk import (
    PortHandler,
    PacketHandler,
    GroupBulkWrite,
    GroupBulkRead,
    COMM_SUCCESS,
    DXL_LOBYTE,
    DXL_LOWORD,
    DXL_HIBYTE,
    DXL_HIWORD,
)

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

# Convert servo units into degrees for readability
# Max for units is 4095, which is 360 degrees
DEGREE_TO_UNIT: float = 4095 / 360.0


def degrees_to_units(degree: int) -> int:
    return int(degree * DEGREE_TO_UNIT)


def units_to_degrees(position: int) -> int:
    return int(position / DEGREE_TO_UNIT)


class Servos:
    def __init__(
        self,
        servos: Dict[str, Servo] = HPARAMS["servos"],
        protocol_version: float = HPARAMS["protocol_version"],
        baudrate: int = HPARAMS["baudrate"],
        device_name: str = HPARAMS["device_name"],
        addr_torque_enable: int = HPARAMS["addr_torque_enable"],
        addr_goal_position: int = HPARAMS["addr_goal_position"],
        addr_present_position: int = HPARAMS["addr_present_position"],
        torque_enable: int = HPARAMS["torque_enable"],
        torque_disable: int = HPARAMS["torque_disable"],
    ):
        self.servos: List[Servo] = []
        for name, servo in servos.items():
            log.debug(f"---- Initialize servo {name} ----")
            log.debug(f"id: {servo.id}")
            log.debug(f"range: {servo.range}")
            log.debug(f"description: {servo.desc}")
            self.servos.append(servo)
        self.num_servos: int = len(self.servos)  # Number of servos to control

        # Dynamixel communication parameters
        self.protocol_version = (
            protocol_version  # DYNAMIXEL Protocol version (1.0 or 2.0)
        )
        self.baudrate = baudrate  # Baudrate for DYNAMIXEL communication
        self.device_name = (
            device_name  # Name of the device (port) where DYNAMIXELs are connected
        )
        self.addr_torque_enable = (
            addr_torque_enable  # Address for Torque Enable control table in DYNAMIXEL
        )
        self.addr_goal_position = (
            addr_goal_position  # Address for Goal Position control table in DYNAMIXEL
        )
        self.addr_present_position = addr_present_position  # Address for Present Position control table in DYNAMIXEL
        self.torque_enable = torque_enable  # Value to enable the torque
        self.torque_disable = torque_disable  # Value to disable the torque

        # Initialize DYNAMIXEL communication
        self.port_handler = PortHandler(self.device_name)
        self.packet_handler = PacketHandler(self.protocol_version)
        if not self.port_handler.openPort():
            log.error("Failed to open the port")
            exit()
        if not self.port_handler.setBaudRate(self.baudrate):
            log.error("Failed to change the baudrate")
            exit()
        self.group_bulk_write = GroupBulkWrite(self.port_handler, self.packet_handler)
        self.group_bulk_read = GroupBulkRead(self.port_handler, self.packet_handler)

    def _write_position(self, positions: List[int]) -> str:
        msg: str = ""
        # Enable torque for all servos and add goal position to the bulk write parameter storage
        for i, pos in enumerate(positions):
            pos = degrees_to_units(pos)
            dxl_id = self.servos[i].id
            clipped = min(max(pos, self.servos[i].range[0]), self.servos[i].range[1])

            dxl_comm_result, dxl_error = self.packet_handler.write1ByteTxRx(
                self.port_handler, dxl_id, self.addr_torque_enable, self.torque_enable
            )
            if dxl_comm_result != COMM_SUCCESS:
                msg += f"ERROR: {self.packet_handler.getTxRxResult(dxl_comm_result)}"
                raise Exception(msg)
            elif dxl_error != 0:
                msg += f"ERROR: {self.packet_handler.getRxPacketError(dxl_error)}"
                raise Exception(msg)

            self.group_bulk_write.addParam(
                dxl_id,
                self.addr_goal_position,
                4,
                [
                    DXL_LOBYTE(DXL_LOWORD(clipped)),
                    DXL_HIBYTE(DXL_LOWORD(clipped)),
                    DXL_LOBYTE(DXL_HIWORD(clipped)),
                    DXL_HIBYTE(DXL_HIWORD(clipped)),
                ],
            )

        # Write goal position
        dxl_comm_result = self.group_bulk_write.txPacket()
        if dxl_comm_result != COMM_SUCCESS:
            msg += f"ERROR: {self.packet_handler.getTxRxResult(dxl_comm_result)}"
            raise Exception(msg)

        # Clear bulk write parameter storage
        self.group_bulk_write.clearParam()

    def _read_pos(self) -> List[int]:
        msg: str = ""
        # Add present position value to the bulk read parameter storage
        for i in range(self.num_servos):
            dxl_id = self.servos[i].id
            dxl_addparam_result = self.group_bulk_read.addParam(
                dxl_id, self.addr_present_position, 4
            )
            if not dxl_addparam_result:
                msg += f"ERROR: [ID:{dxl_id}] groupBulkRead addparam failed\n"
                raise Exception(msg)

        # Read present position
        dxl_comm_result = self.group_bulk_read.txRxPacket()
        if dxl_comm_result != COMM_SUCCESS:
            msg += f"ERROR: {self.packet_handler.getTxRxResult(dxl_comm_result)}\n"
            raise Exception(msg)

        # Get present position value
        positions = []
        for i in range(self.num_servos):
            dxl_id = self.servos[i].id
            dxl_present_position = self.group_bulk_read.getData(
                dxl_id, self.addr_present_position, 4
            )
            positions.append(units_to_degrees(dxl_present_position))

        # Clear bulk read parameter storage
        self.group_bulk_read.clearParam()

        return positions

    def _disable_torque(self) -> None:
        for servo in self.servos:
            dxl_comm_result, dxl_error = self.packet_handler.write1ByteTxRx(
                self.port_handler,
                servo.id,
                self.addr_torque_enable,
                self.torque_disable,
            )
            if dxl_comm_result != COMM_SUCCESS:
                log.error(
                    f"ERROR: {self.packet_handler.getTxRxResult(dxl_comm_result)}"
                )
            elif dxl_error != 0:
                log.error(f"ERROR: {self.packet_handler.getRxPacketError(dxl_error)}")

    def __del__(self, *args, **kwargs) -> None:
        self._disable_torque()
        self.port_handler.closePort()


@async_task(timeout=HPARAMS["timeout_set_servos"])
async def set_servos(
    action: str,
    servos: Servos,
    pose_dict: Dict[str, Pose] = HPARAMS["poses"],
    move_dict: Dict[str, Move] = HPARAMS["moves"],
    speed: int = HPARAMS["set_servo_speed"],
    duration: int = HPARAMS["set_servo_duration"],
    interval: float = HPARAMS["set_servo_interval"],
) -> Dict[str, Any]:
    log: str = f"Action {action}."
    # Pick the goal position
    desired_pose = pose_dict.get(action, None)
    if desired_pose is not None:
        log += "is a Pose."
        goal_pos = desired_pose.angles
    else:
        desired_move = move_dict.get(action, None)
        if desired_move is not None:
            log += "is a Move."
            move_vector = [x * speed for x in desired_move.vector]
            log += f"Move vector is {move_vector}."
            true_pos = servos._read_pos()
            goal_pos = [move_vector[i] + true_pos[i] for i in range(len(move_vector))]
        else:
            log += "is not valid. Moving to forward position."
            goal_pos = pose_dict["forward"].angles
    log += f"Goal position is {goal_pos}."
    # Move to the goal position over timeout seconds
    duration: timedelta = timedelta(seconds=duration)
    start_time = time.time()
    while True:
        elapsed_time = time.time() - start_time
        if elapsed_time > duration.total_seconds():
            log += f"Action finished after {elapsed_time} seconds."
            break
        true_pos = servos._read_pos()
        # Interpolate between the current position and the goal position
        # based on the fraction of time elapsed
        fraction = elapsed_time / duration.total_seconds()
        interpolated_position = [
            int((goal_pos[i] - true_pos[i]) * fraction + true_pos[i])
            for i in range(len(goal_pos))
        ]
        servos._write_position(interpolated_position)
        distance_to_target: int = sum(
            abs(true_pos[i] - goal_pos[i]) for i in range(len(goal_pos))
        )
        log += f"Distance to target is {distance_to_target}."
        time.sleep(interval)
    true_pos = servos._read_pos()
    log += f"Current position is {true_pos}."
    return {
        "log": log,
        "pos": true_pos,
    }


def test_servos() -> None:
    log.setLevel(logging.DEBUG)
    log.debug("Testing move")
    servos = Servos()
    for name, pose in HPARAMS["poses"].items():
        print(f"Moving to pose {name}")
        result = asyncio.run([set_servos(name, servos)])
        print(result)
        time.sleep(1)


def limp_mode() -> None:
    log.setLevel(logging.DEBUG)
    log.debug("Limp Mode")
    servos = Servos()
    servos._disable_torque()
    while True:
        print(servos._read_pos())


if __name__ == "__main__":
    test_servos()
    # limp_mode()
