import os
import os.path as osp
import json
import yaml
import sys
from io import StringIO


DEFAULT_IMAGE = "https://pbs.twimg.com/profile_images/578844000267816960/6cj6d4oZ_400x400.png"
TEAMS_FILE = "../admin/teams.yaml"

if __name__ == "__main__":
    score_file = sys.argv[1]
    tname = sys.argv[2]
    score = sys.argv[3]

    print(f"Score file is {score_file}")
    print(f"Team is {tname}")
    yaml_score = yaml.safe_load(StringIO(score))
    
    with open(score_file, "r") as f:
        jdata = json.load(f)

    tentry = [team for team in jdata if team["team_name"] == tname]

    with open(TEAMS_FILE, "r") as f:
        tdata = yaml.safe_load(f)

    tdata = [t for t in tdata["teams"] if t["name"] == tname]
    if len(tdata) == 0 or "icon" not in tdata[0]:
        img = DEFAULT_IMAGE
    else:
        img = tdata[0]["icon"]

    if len(tentry) > 0:
        if yaml_score["avg_score"] > tentry[0]["team_score"]:
            tentry[0]["team_score"] = yaml_score["avg_score"]
        tentry[0]["team_image"] = img
    else:

        jdata.append({
            "team_name": tname,
            "team_score": yaml_score["avg_score"],
            "team_image": img,
            "submission_date": "2022/11/23"
        })


    with open(score_file, "w+") as f:
        json.dump(jdata, f, indent=2)
