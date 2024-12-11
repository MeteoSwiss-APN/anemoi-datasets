# (C) Copyright 2024 Anemoi contributors.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
#
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.


import datetime
import logging

LOG = logging.getLogger(__name__)


class Time:
    @classmethod
    def from_coordinates(cls, coordinates):
        time_coordinate = [c for c in coordinates if c.is_time]
        step_coordinate = [c for c in coordinates if c.is_step]
        date_coordinate = [c for c in coordinates if c.is_date]

        if len(date_coordinate) == 0 and len(time_coordinate) == 1 and len(step_coordinate) == 1:
            return ForecasstFromValidTimeAndStep(step_coordinate[0])

        if len(date_coordinate) == 0 and len(time_coordinate) == 1 and len(step_coordinate) == 0:
            return Analysis()

        if len(date_coordinate) == 0 and len(time_coordinate) == 0 and len(step_coordinate) == 0:
            return Constant()

        if len(date_coordinate) == 1 and len(time_coordinate) == 1 and len(step_coordinate) == 0:
            return ForecastFromValidTimeAndBaseTime(date_coordinate[0])

        if len(date_coordinate) == 1 and len(time_coordinate) == 0 and len(step_coordinate) == 1:
            return ForecastFromBaseTimeAndDate(date_coordinate[0], step_coordinate[0])

        if len(date_coordinate) == 1 and len(time_coordinate) == 1 and len(step_coordinate) == 1:
            return ForecastFromValidTimeAndStep(time_coordinate[0], step_coordinate[0], date_coordinate[0])

        LOG.error("")
        LOG.error(f"{len(date_coordinate)} date_coordinate")
        for c in date_coordinate:
            LOG.error("    %s %s %s %s", c, c.is_date, c.is_time, c.is_step)
            # LOG.error('    %s', c.variable)

        LOG.error("")
        LOG.error(f"{len(time_coordinate)} time_coordinate")
        for c in time_coordinate:
            LOG.error("    %s %s %s %s", c, c.is_date, c.is_time, c.is_step)
            # LOG.error('    %s', c.variable)

        LOG.error("")
        LOG.error(f"{len(step_coordinate)} step_coordinate")
        for c in step_coordinate:
            LOG.error("    %s %s %s %s", c, c.is_date, c.is_time, c.is_step)
            # LOG.error('    %s', c.variable)

        raise NotImplementedError(f"{len(date_coordinate)=} {len(time_coordinate)=} {len(step_coordinate)=}")


class Constant(Time):

    def fill_time_metadata(self, coords_values, metadata):
        return None


class Analysis(Time):

    def fill_time_metadata(self, time, metadata):
        metadata["date"] = time.strftime("%Y%m%d")
        metadata["time"] = time.strftime("%H%M")
        metadata["step"] = 0


class ForecastFromValidTimeAndStep(Time):

    def __init__(self, time_coordinate, step_coordinate, date_coordinate=None):
        self.time_coordinate_name = time_coordinate.variable.name
        self.step_coordinate_name = step_coordinate.variable.name
        self.date_coordinate_name = date_coordinate.variable.name if date_coordinate else None

    def fill_time_metadata(self, time, metadata):
        step = metadata.pop(self.step_name)
        assert isinstance(step, datetime.timedelta)
        base = time - step

        hours = step.total_seconds() / 3600
        assert int(hours) == hours

        metadata["date"] = base.strftime("%Y%m%d")
        metadata["time"] = base.strftime("%H%M")
        metadata["step"] = int(hours)

        # When date is present, it should be compatible with time and step

        if self.date_coordinate_name is not None:
            # Not sure that this is the correct assumption
            assert coords_values[self.date_coordinate_name] == base_datetime, (
                coords_values[self.date_coordinate_name],
                base_datetime,
            )

        return valid_datetime


class ForecastFromValidTimeAndBaseTime(Time):
    def __init__(self, date_coordinate):
        self.date_coordinate = date_coordinate

    def fill_time_metadata(self, time, metadata):

        step = time - self.date_coordinate

        hours = step.total_seconds() / 3600
        assert int(hours) == hours

        metadata["date"] = self.date_coordinate.single_value.strftime("%Y%m%d")
        metadata["time"] = self.date_coordinate.single_value.strftime("%H%M")
        metadata["step"] = int(hours)


class ForecastFromBaseTimeAndDate(Time):
    def __init__(self, date_coordinate, step_coordinate):
        self.date_coordinate = date_coordinate
        self.step_coordinate = step_coordinate

    def fill_time_metadata(self, time, metadata):
        metadata["date"] = time.strftime("%Y%m%d")
        metadata["time"] = time.strftime("%H%M")
        hours = metadata[self.step_coordinate.name].total_seconds() / 3600
        assert int(hours) == hours
        metadata["step"] = int(hours)
