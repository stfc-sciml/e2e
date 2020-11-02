import os
import platform
import psutil
import socket
import cpuinfo
import pynvml as nv


def bytesto(bytes, to, bsize=1024):
    size = {'k': 1, 'm': 2, 'g': 3, 't': 4, 'p': 5, 'e': 6}
    r = float(bytes)
    for i in range(size[to]):
        r = r / bsize
    return (r)


class HostSpec:

    def __init__(self, pid=None, per_device=False):
        self._per_device = per_device
        self._process = psutil.Process(pid)

    @property
    def name(self):
        return os.name

    @property
    def system(self):
        return platform.system()

    @property
    def node_name(self):
        return socket.gethostname()

    @property
    def ip_address(self):
        return socket.gethostbyname(self.node_name)

    @property
    def release(self):
        return platform.release()

    @property
    def num_cores(self):
        return psutil.cpu_count()

    @property
    def total_memory(self):
        mem = psutil.virtual_memory()
        return mem.total

    @property
    def cpu_percent(self):
        info = self._process.cpu_percent()
        return info

    @property
    def cpu_info(self):
        info = cpuinfo.get_cpu_info()
        keys = ['brand', 'arch', 'vendor_id', 'hz_advertised', 'hz_actual', 'model', 'family']
        info = {key: value for key, value in info.items() if key in keys}
        info['num_cores'] = self.num_cores
        return info

    @property
    def disk_io(self):
        try:
            info = self._process.io_counters()
            for child in self._process.children(recursive=True):
                child_info = child.disk_io_counters()
        except AttributeError:
            return {}

    @property
    def net_io(self):
        info = self._process.net_io_counters(pernic=self._per_device)
        if self._per_device:
            return {key: {k: v for k, v in value._asdict().items()} for key, value in info.items()}
        else:
            return {k: v for k, v in info._asdict().items()}

    @property
    def memory(self):
        memory_props = dict(self._process.virtual_memory()._asdict())

        metrics = {}
        metrics['free'] = bytesto(memory_props['free'], 'm')
        metrics['used'] = bytesto(memory_props['used'], 'm')
        metrics['available'] = bytesto(memory_props['available'], 'm')
        metrics['utilization'] = memory_props['percent']
        return metrics

    def get_sys_state(self):
        state = {}
        state['cpu'] = dict(percent=self.cpu_percent)
        state['memory'] = self.memory
        state['net'] = self.net_io
        state['disk'] = self.disk_io
        return state

    def get_sys_info(self):
        info = {}
        info['node_name'] = self.node_name
        info['release'] = self.release
        info['system'] = self.system
        info['cpu'] = self.cpu_info
        info['memory'] = dict(total=self.total_memory)
        info['net'] = dict(ip=self.ip_address)
        return info


class DeviceSpec:

    def __init__(self, index):
        try:
            nv.nvmlInit()
            self._handle = nv.nvmlDeviceGetHandleByIndex(index)
        except nv.NVMLError_LibraryNotFound:
            raise RuntimeError(f"Cannot find GPU with index {index}")

    @property
    def uuid(self):
        """ NVIDIA device UUID """
        return nv.nvmlDeviceGetUUID(self._handle).decode()

    @property
    def name(self):
        """ NVIDIA device name """
        return nv.nvmlDeviceGetName(self._handle).decode()

    @property
    def brand(self):
        """ Device brand name as a string

        This function maps the device code to a string representation using the
        following enum:

            NVML_BRAND_UNKNOWN = 0
            NVML_BRAND_QUADRO = 1
            NVML_BRAND_TESLA = 2
            NVML_BRAND_NVS = 3
            NVML_BRAND_GRID = 4
            NVML_BRAND_GEFORCE = 5
            NVML_BRAND_TITAN = 6
        """
        brand_enum = nv.nvmlDeviceGetBrand(self._handle)

        if brand_enum == 1:
            return 'Quadro'
        elif brand_enum == 2:
            return 'Tesla'
        elif brand_enum == 3:
            return 'NVS'
        elif brand_enum == 4:
            return 'Grid'
        elif brand_enum == 5:
            return 'GeForce'
        elif brand_enum == 6:
            return 'Titan'
        else:
            return 'Unknown'

    @property
    def minor_number(self):
        return nv.nvmlDeviceGetMinorNumber(self._handle)

    @property
    def is_multigpu_board(self):
        return nv.nvmlDeviceGetMultiGpuBoard(self._handle)

    @property
    def utilization_rates(self):
        rates = nv.nvmlDeviceGetUtilizationRates(self._handle)
        return dict(gpu=rates.gpu, memory=rates.memory)

    @property
    def memory(self):
        """ Total, free, and used memory in bytes"""
        info = nv.nvmlDeviceGetMemoryInfo(self._handle)
        return dict(free=info.free, total=info.total, used=info.used)

    @property
    def power_usage(self):
        """ Power usage for the device in milliwatts

        From the NVIDIA documentation:
         - On Fermi and Kepler GPUs the reading is accurate to within +/- 5% of current power draw.
        """
        return nv.nvmlDeviceGetPowerUsage(self._handle)

    def get_device_state(self):
        state = {}
        state['power'] = self.power_usage
        state['memory'] = dict(utilization=self.utilization_rates['memory'], used=self.memory['used'], free=self.memory['free'])
        state['gpu'] = dict(utilization=self.utilization_rates['gpu'])
        return state

    def get_device_info(self):
        info = {}
        info['memory'] = dict(total=self.memory['total'])
        info['name'] = self.name
        info['brand'] = self.brand
        info['multi_board'] = self.is_multigpu_board
        info['uuid'] = self.uuid
        return info
