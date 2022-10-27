import logging
import os
from typing import List

from fastapi import FastAPI, HTTPException

from exclusion.components import ExclusionInterval, ExclusionPoint
from exclusion.db import MassIntervalTree as ExclusionList

_log = logging.getLogger(__name__)
_log.setLevel(logging.INFO)

app = FastAPI()

active_exclusion_list = ExclusionList()
#active_exclusion_list.add(ExclusionInterval())


def get_pickle_path(exclusion_list_name: str) -> str:
    return os.path.join('data', 'pickles', exclusion_list_name + '.pkl')


@app.post("/exclusion", status_code=201)
async def new_exclusion_list():
    _log.info(f'Setup Exclusion List')
    active_exclusion_list.clear()
    return True


@app.post("/exclusion/save", status_code=200)
async def save_active_exclusion_list(exclusion_list_name: str):
    pickle_path = get_pickle_path(exclusion_list_name)
    _log.info(f'Saving active exclusion list to: {pickle_path}')

    if os.path.exists(pickle_path):
        _log.warning(f'{pickle_path} already exists. Overriding.')

    try:
        active_exclusion_list.save(pickle_path)
    except Exception as e:
        _log.error(f'Error when saving exclusion list: {e}')
        raise HTTPException(status_code=500, detail='Error saving active exclusion list.')


@app.post("/exclusion/load", status_code=204)
async def save_active_exclusion_list(exclusion_list_name: str):
    pickle_path = get_pickle_path(exclusion_list_name)
    _log.info(f'Loading active exclusion list from: {pickle_path}')

    if os.path.exists(pickle_path) is False:
        raise HTTPException(status_code=404, detail=f"exclusion list with name: {exclusion_list_name} not found.")

    try:
        active_exclusion_list.load(pickle_path)
    except Exception as e:
        _log.error(f'Exception when loading exclusion list: {e}')
        raise HTTPException(status_code=500, detail='Error loading active exclusion list.')


@app.get("/exclusion/interval", response_model=List[ExclusionInterval], status_code=200)
async def get_interval(id: str | None = None, charge: int | None = None, min_mass: float | None = None,
                       max_mass: float | None = None,
                       min_rt: float | None = None, max_rt: float | None = None, min_ook0: float | None = None,
                       max_ook0: float | None = None, min_intensity: float | None = None,
                       max_intensity: float | None = None):
    ex_interval = ExclusionInterval(id=id, charge=charge, min_mass=min_mass, max_mass=max_mass, min_rt=min_rt,
                                    max_rt=max_rt, min_ook0=min_ook0, max_ook0=max_ook0, min_intensity=min_intensity,
                                    max_intensity=max_intensity)

    return [interval for interval in active_exclusion_list.query_by_interval(ex_interval)]


@app.post("/exclusion/interval", status_code=204)
async def add_interval(exclusion_interval: ExclusionInterval):
    active_exclusion_list.add(exclusion_interval)


# TODO: Return deleted Items?
@app.delete("/exclusion/interval", status_code=204)
async def remove_interval(exclusion_list: ExclusionInterval):
    return active_exclusion_list.remove(exclusion_list)


@app.get("/exclusion/point", status_code=200)
async def get_point(charge: int | None = None, mass: float | None = None,
                    rt: float | None = None, ook0: float | None = None, intensity: float | None = None):
    ex_point = ExclusionPoint(charge=charge, mass=mass, rt=rt, ook0=ook0, intensity=intensity)
    return active_exclusion_list.is_excluded(ex_point)


@app.get("/exclusion/stats", status_code=200)
async def get_statistics():
    return active_exclusion_list.stats()
