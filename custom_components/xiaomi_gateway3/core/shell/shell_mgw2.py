import base64

from .base import ShellMultimode
from .shell_arm import ShellARM

TAR_DATA = "tar -czOC /data mha_master miio storage zigbee devices.txt gatewayInfoJson.info 2>/dev/null | base64"


# noinspection PyAbstractClass
class ShellMGW2(ShellARM, ShellMultimode):
    model = "mgw2"

    async def tar_data(self):
        raw = await self.exec(TAR_DATA, as_bytes=True)
        return base64.b64decode(raw)

    @property
    def mesh_db(self) -> str:
        return "/data/local/miio_bt/mible_local.db"

    @property
    def mesh_group_table(self) -> str:
        return "mesh_group_v3"

    @property
    def mesh_device_table(self) -> str:
        return "mesh_device_v3"

    async def get_wlan_mac(self) -> str:
        icmd = "MYPTS=`tty | sed 's/^\/dev\///'`; " + \
               "RADDR=`who | grep \"$MYPTS\" | awk '{print $7;}' | tr -d '[]'`; " + \
               "LADDR=`netstat -t | grep \"$RADDR\" | awk '{print $4;}' | sed 's/::ffff://' | cut -d: -f1`; " + \
                "ip -o a | grep \"inet $LADDR\" | awk '{print $2;}'"

        iface = await self.exec(icmd)
        iface = iface.strip()
        iface ="wlan0" if not iface in ("eth0", "wlan0") else iface
        raw = await self.read_file("/sys/class/net/" + iface + "/address")
        return raw.decode().rstrip().replace(":", "")
