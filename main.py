import logging
import os
from dataclasses import dataclass
from typing import List

from fastapi import FastAPI, HTTPException
from kafka import KafkaConsumer

from src.apio.exclusion.consumer import ExclusionListConfig, create_consumer, ExclusionListWorker
from src.apio.exclusion.components import ExclusionInterval, ExclusionPoint
from src.apio.exclusion.db import MassIntervalTree as ExclusionList


_log = logging.getLogger(__name__)
_log.setLevel(logging.INFO)

app = FastAPI()


@dataclass
class ApioExclusionList:
    exclusion_list: ExclusionList
    ex_config: ExclusionListConfig
    worker: ExclusionListWorker


#TODO: Remove
exlists = {1:ApioExclusionList(ExclusionList(), {'testing':'stats'}, None)}
exlists[1].exclusion_list.add(ExclusionInterval())


def get_apio_exclusion_list(id):
    apio_exclusion_list = exlists.get(id)
    if apio_exclusion_list is None:
        _log.warning(f'Exclusion List with ID: {id} does not exist!')
        raise HTTPException(status_code=404, detail=f"exclusion list with id: {id} not found.")
    return apio_exclusion_list


def get_exclusion_list(id):
    return get_apio_exclusion_list(id).exclusion_list


def get_config(id):
    return get_apio_exclusion_list(id).ex_config


def get_worker(id):
    return get_apio_exclusion_list(id).worker


def get_pickle_path(exclusion_id: int) -> str:
    return os.path.join('data', 'pickles', str(exclusion_id) + '.pkl')


@app.post("/apio/ex/setup")
async def setup_exclusion_list(exclusion_id: int, ex_config: ExclusionListConfig):
    """
    Initializes the APIO apio list with exclusion_id. If there is a saved apio list
    with a matching id, then the this excluded list is loaded from the file.

    :param exclusion_id: the apio list identifier
    :return: True if succeeded setup; False if failed setup
    """
    _log.info(f'Setup Exclusion List: {exclusion_id}')
    ex_list = ExclusionList()
    worker = ExclusionListWorker(ex_list, ex_config)
    exlists[exclusion_id] = ApioExclusionList(ex_list, ex_config, worker)

    pickle_path = get_pickle_path(exclusion_id)
    if os.path.exists(pickle_path):
        _log.info(f'loading apio list from: {pickle_path}')
        try:
            ex_list.load(pickle_path)
        except Exception as e:
            _log.error(f'Exception when loading apio list: {e}')
            raise HTTPException(status_code=500,
                                detail=f"Error Loading exclusion list with id: {exclusion_id} from file.")
    else:
        _log.info(f'No existing Exclusion List found at: {pickle_path}')

    worker.start()
    return True

@app.get("/apio/ex/setup")
async def exclusion_list_status():
    """
    Initializes the APIO apio list with exclusion_id. If there is a saved apio list
    with a matching id, then the this excluded list is loaded from the file.

    :param exclusion_id: the apio list identifier
    :return: True if succeeded setup; False if failed setup
    """
    return list(exlists.keys())


@app.delete("/apio/ex/setup")
async def cleanup_exclusion_list(exclusion_id: int):
    """
    de-initializes the APIO apio list with exclusion_id and saves the current list as a pickled object.

    :param exclusion_id: the apio list identifier
    :return: True if succeeded setup; False if failed setup
    """
    _log.info(f'Cleanup Exclusion List: {exclusion_id}')

    exlist = get_exclusion_list(exclusion_id)
    worker = get_worker(exclusion_id)


    pickle_path = get_pickle_path(exclusion_id)
    _log.info(f'saving apio list to: {pickle_path}')

    if os.path.exists(pickle_path) is False:
        _log.warning(f'Exclusion List with ID: {exclusion_id} already exists. Saving over old file!')
        return True

    try:
        exlist.save(pickle_path)
    except Exception as e:
        _log.error(f'Exception when saving apio list: {e}')
        raise HTTPException(status_code=500, detail=f"Error Saving exclusion list with id: {exclusion_id} from file.")

    exlist.clear()
    worker.join()
    exlists.pop(exclusion_id)

    return True


@app.get("/apio/ex/interval", response_model=List[ExclusionInterval])
async def get_interval(exclusion_id: int, id: str | None = None, charge: int | None = None, min_mass: float | None = None, max_mass: float | None = None,
                         min_rt: float | None = None, max_rt: float | None = None, min_ook0: float | None = None,
                         max_ook0: float | None = None, min_intensity: float | None = None, max_intensity: float | None = None):

    ex_interval = ExclusionInterval(id=id, charge=charge, min_mass=min_mass, max_mass=max_mass, min_rt=min_rt,
                                    max_rt=max_rt, min_ook0=min_ook0, max_ook0=max_ook0, min_intensity=min_intensity,
                                    max_intensity=max_intensity)

    exlist = get_exclusion_list(exclusion_id)

    return [interval for interval in exlist.query_by_interval(ex_interval)]


@app.delete("/apio/ex/interval")
async def remove_interval(exclusion_id: int, ex_interval: ExclusionInterval):
    exlist = get_exclusion_list(exclusion_id)
    return exlist.remove(ex_interval)


@app.post("/apio/ex/interval")
async def add_interval(exclusion_id: int, ex_interval: ExclusionInterval):
    exlist = get_exclusion_list(exclusion_id)
    exlist.add(ex_interval)
    return True


@app.get("/apio/ex/point")
async def get_point(exclusion_id: int, charge: int | None = None, mass: float | None = None,
                         rt: float | None = None, ook0: float | None = None, intensity: float | None = None):
    ex_point = ExclusionPoint(charge=charge, mass=mass, rt=rt, ook0=ook0, intensity=intensity)
    exlist = get_exclusion_list(exclusion_id)
    return exlist.is_excluded(ex_point)


@app.get("/apio/ex/stats")
async def get_statistics(exclusion_id: int):
    return {**get_config(exclusion_id).dict(), **get_exclusion_list(exclusion_id).stats()}
