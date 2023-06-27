from dataclasses import dataclass
from typing import Optional

from reamber.algorithms.generate import full_ln
from reamber.osu.OsuHit import OsuHit
from reamber.osu.OsuMap import OsuMap
from reamber.algorithms.playField import PlayField
from reamber.algorithms.playField.parts import *
from pathlib import Path
from zipfile import ZipFile
from ..file import download_map
from ..schema import SayoBeatmap
import os
import shutil
import asyncio
import numpy

osu_path = Path() / "data" / "osu"
if not osu_path.exists():
    osu_path.mkdir(parents=True, exist_ok=True)


@dataclass
class Options:
    rate: Optional[float]
    end_rate: Optional[float]
    od: Optional[float]
    set: Optional[int]
    map: Optional[int] = None
    sayo_info: Optional[SayoBeatmap] = None
    nsv: bool = False
    nln: bool = False
    fln: bool = False
    step: float = 0.05
    gap: float = 150
    thres: float = 100


async def generate_preview_pic(file: Path):
    m = OsuMap.read_file(str(file.absolute()))
    pf = (
            PlayField(m, padding=30)
            + PFDrawColumnLines()
            + PFDrawBeatLines()
            + PFDrawBpm(x_offset=30, y_offset=0)
            + PFDrawSv(y_offset=0)
            + PFDrawNotes()
    )
    pf.export_fold(max_height=1000).save("data/osu/preview.png")
    return Path("data/osu/preview.png")


async def convert_mania_map(options: Options) -> Optional[Path]:
    path = osu_path / f"{options.set}"
    osz_file = await download_map(options.set)
    if not osz_file:
        return
    with ZipFile(osz_file.absolute()) as my_zip:
        my_zip.extractall(path)
    os.remove(osz_file)
    for i in options.sayo_info.data.bid_data:
        if i.bid == options.map:
            audio_file_name = i.audio
            audio_name = audio_file_name[:-4]
            audio_type = audio_file_name[-4:]
            break
    else:
        raise Exception('小夜api有问题啊')
    if options.rate:
        if options.rate > 10:
            options.rate = 10
        end = options.end_rate if options.end_rate else options.rate + 0.01
        if end > 10:
            end = 10.1
        if options.step and abs(options.step) < 0.05:
            options.step = 0.05 if options.step > 0 else -0.05
        if not options.step:
            options.step = 0.05
        tasks = []
        for rate in numpy.arange(options.rate, end, options.step):
            new_audio_path = path / (audio_name + f'x{rate:.2f}' + audio_type)
            tasks.append(asyncio.create_subprocess_shell(
                f'ffmpeg -i "{(path / audio_file_name).absolute()}" -threads 4 -filter:a "atempo={rate}" -b:a 128k -vn -y '
                f'"{new_audio_path.absolute()}" -loglevel quiet'
            ))
        await asyncio.gather(*tasks)
    osu_ls = list()
    for file in path.rglob('*.osu'):
        osu = OsuMap.read_file(str(file.absolute()))
        if options.rate:
            if osu.audio_file_name != audio_file_name:
                continue
            for rate in numpy.arange(options.rate, end, options.step):
                rate = round(rate, 2)
                osu_new = osu.rate(rate)
                osu_new.version += f' x{rate}'
                osu_new.audio_file_name = audio_name + f'x{rate:.2f}' + audio_type
                osu_ls.append([file.stem + f'x{rate}', osu_new])
        else:
            osu_new = osu.rate(1)
            osu_ls.append([file.stem, osu_new])
    for i in osu_ls:
        if options.fln:
            i[1] = full_ln(i[1], gap=options.gap, ln_as_hit_thres=options.thres)
            i[1].version += ' (FULL LN)'
            i[0] += ' (FULL LN)'
        if options.nsv:
            i[1].svs = i[1].svs[:0]
            i[1].bpms = i[1].bpms[:1]
            i[1].version += " NSV"
            i[0] += " NSV"
        if options.nln:
            for ln in i[1].holds:
                i[1].hits = i[1].hits.append(OsuHit(ln.offset, int(ln.column)))
            i[1].holds.df = i[1].holds.df[:0]
            i[1].version += " NLN"
            i[0] += " NLN"
        if options.od is not None:
            i[1].overall_difficulty = options.od
            i[1].version += f" OD {options.od}"
            i[0] += f" od{options.od}"
    for filename, osu in osu_ls:
        osu.write_file(path / f"{filename}.osu")

    with ZipFile(path.parent / osz_file.name, 'w') as my_zip:
        for file in path.rglob('*'):
            my_zip.write(file, os.path.relpath(file, path))
    shutil.rmtree(path)
    return path.parent / osz_file.name
