# (C) Datadog, Inc. 2021-present
# All rights reserved
# Licensed under a 3-clause BSD style license (see LICENSE)
from __future__ import annotations

from typing import Any, Mapping, Optional, Sequence

from pydantic import BaseModel, root_validator, validator

from datadog_checks.base.utils.functions import identity
from datadog_checks.base.utils.models import validation

from . import defaults, validators


class CreateMount(BaseModel):
    class Config:
        allow_mutation = False

    host: Optional[str]
    mountpoint: Optional[str]
    password: Optional[str]
    share: Optional[str]
    type: Optional[str]
    user: Optional[str]


class InstanceConfig(BaseModel):
    class Config:
        allow_mutation = False

    all_partitions: Optional[bool]
    blkid_cache_file: Optional[str]
    create_mounts: Optional[Sequence[CreateMount]]
    device_exclude: Optional[Sequence[str]]
    device_include: Optional[Sequence[str]]
    device_tag_re: Optional[Mapping[str, Any]]
    empty_default_hostname: Optional[bool]
    file_system_exclude: Optional[Sequence[str]]
    file_system_include: Optional[Sequence[str]]
    include_all_devices: Optional[bool]
    min_collection_interval: Optional[float]
    min_disk_size: Optional[float]
    mount_point_exclude: Optional[Sequence[str]]
    mount_point_include: Optional[Sequence[str]]
    service: Optional[str]
    service_check_rw: Optional[bool]
    tag_by_filesystem: Optional[bool]
    tag_by_label: Optional[bool]
    tags: Optional[Sequence[str]]
    timeout: Optional[int]
    use_mount: bool

    @root_validator(pre=True)
    def _initial_validation(cls, values):
        return validation.core.initialize_config(getattr(validators, 'initialize_instance', identity)(values))

    @validator('*', pre=True, always=True)
    def _ensure_defaults(cls, v, field):
        if v is not None or field.required:
            return v

        return getattr(defaults, f'instance_{field.name}')(field, v)

    @validator('*')
    def _run_validations(cls, v, field):
        if not v:
            return v

        return getattr(validators, f'instance_{field.name}', identity)(v, field=field)

    @root_validator(pre=False)
    def _final_validation(cls, values):
        return validation.core.finalize_config(getattr(validators, 'finalize_instance', identity)(values))
