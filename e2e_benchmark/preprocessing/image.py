import os
import numpy as np
import xarray as xr
from scipy import interpolate


class ImageLoader:

    def __init__(self, path, engine='h5netcdf'):
        self.path = path
        self._engine = engine

    def load_radiances(self, view='an'):
        rads = [
            self.load_radiance_channel(
                self.path,
                i,
                view) for i in range(
                1,
                7)]
        rads = xr.merge(rads)
        return rads

    def load_irradiances(self, view='an'):
        irradiances = {}
        for i in range(1, 7):
            name = 'S{}_solar_irradiance_{}'.format(i, view)
            file_name = os.path.join(
                self.path, 'S{}_quality_{}.nc'.format(
                    i, view))
            irradiance = xr.open_dataset(file_name, engine=self._engine)[name][:].data[0]
            irradiances[name] = irradiance
        return irradiances

    def load_reflectance(self, view='an'):
        refs = [
            self.load_reflectance_channel(
                self.path,
                i,
                view) for i in range(
                1,
                7)]
        refs = xr.merge(refs)
        return refs

    def load_reflectance_channel(self, path, channel_num, view='an'):
        rads = self.load_radiance_channel(path, channel_num, view)
        names = {name: name.replace('radiance', 'reflectance')
                 for name in rads}
        rads = rads.rename(names)
        irradiances = self.load_irradiances(view)
        geometry = self.load_geometry()

        solar_zenith = geometry.solar_zenith_tn[:]
        solar_zenith = np.nan_to_num(solar_zenith, 0.0)

        x = (np.arange(rads.dims['columns']) - rads.track_offset) * float(
            rads.resolution.split()[1]) / float(geometry.resolution.split()[1]) + geometry.track_offset
        y = np.arange(rads.dims['rows']) * float(rads.resolution.split()[2]) / \
            float(geometry.resolution.split()[2]) + geometry.start_offset

        f = interpolate.RectBivariateSpline(np.arange(
            geometry.dims['rows']), np.arange(geometry.dims['columns']), solar_zenith)
        solar_zenith = f(y, x)

        DTOR = 0.017453292
        mu0 = np.where(solar_zenith < 90, np.cos(DTOR * solar_zenith), 1.0)

        name = 'S{}_reflectance_{}'.format(channel_num, view)
        rads[name] = rads[name] / \
            (irradiances[name[:2] +
                         '_solar_irradiance_{}'.format(view)] * mu0) * np.pi
        return rads

    def load_radiance_channel(self, path, channel_num, view='an'):
        excluded_vars = [
            "S{}_exception_{}".format(channel_num, view),
            "S{}_radiance_orphan_{}".format(channel_num, view),
            "S{}_exception_orphan_{}".format(channel_num, view)
        ]

        path = os.path.join(
            path, 'S{}_radiance_{}.nc'.format(
                channel_num, view))
        radiance = xr.open_dataset(
            path, decode_times=False, engine=self._engine, drop_variables=excluded_vars)
        return radiance

    def load_bts(self, view='in'):
        bts = [self.load_bt_channel(self.path, i, view) for i in range(7, 10)]
        bts = xr.merge(bts)
        return bts

    def load_bt_channel(self, path, channel_num, view='in'):
        excluded_vars = [
            "S{}_exception_{}".format(channel_num, view),
            "S{}_BT_orphan_{}".format(channel_num, view),
            "S{}_exception_orphan_{}".format(channel_num, view)
        ]

        path = os.path.join(path, 'S{}_BT_{}.nc'.format(channel_num, view))
        bt = xr.open_dataset(path, decode_times=False, engine=self._engine,
                             drop_variables=excluded_vars)
        return bt

    def load_flags(self):
        flags_path = os.path.join(self.path, 'flags_in.nc')
        excluded = [
            'confidence_orphan_in',
            'pointing_orphan_in',
            'pointing_in',
            'cloud_orphan_in',
            'bayes_orphan_in',
            'probability_cloud_dual_in']
        flags = xr.open_dataset(flags_path, decode_times=False, engine=self._engine,
                                drop_variables=excluded)

        flag_masks = flags.confidence_in.attrs['flag_masks']
        flag_meanings = flags.confidence_in.attrs['flag_meanings'].split()
        flag_map = dict(zip(flag_meanings, flag_masks))

        expanded_flags = {}
        for key, bit in flag_map.items():
            msk = flags.confidence_in & bit
            msk = xr.where(msk > 0, 1, 0)
            expanded_flags[key] = msk

        return flags.assign(**expanded_flags)

    def load_geometry(self):
        path = os.path.join(self.path, 'geometry_tn.nc')
        geo = xr.open_dataset(path, decode_times=False, engine=self._engine)
        return geo

    def load_met(self):
        met_path = os.path.join(self.path, 'met_tx.nc')
        met = xr.open_dataset(met_path, decode_times=False, engine=self._engine)
        met = met[['total_column_water_vapour_tx', 'cloud_fraction_tx',
                   'skin_temperature_tx', 'sea_surface_temperature_tx',
                   'total_column_ozone_tx', 'soil_wetness_tx',
                   'snow_albedo_tx', 'snow_depth_tx', 'sea_ice_fraction_tx',
                   'surface_pressure_tx']]
        met = met.squeeze()
        return met

    def load_geodetic(self, view='an'):
        flags_path = os.path.join(self.path, 'geodetic_{}.nc'.format(view))
        excluded = ['elevation_orphan_an', 'elevation_an',
                    'latitude_orphan_an', 'longitude_orphan_an']
        flags = xr.open_dataset(flags_path, decode_times=False, engine=self._engine,
                                drop_variables=excluded)
        return flags
