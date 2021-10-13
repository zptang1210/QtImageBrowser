
toGreyscaleItem = {"preset": True, "name": "to greyscale", "description": "convert images to greyscale", "file": "utils/transformers/presets/preset_toGreyscale.txt"}
stabilizedTrackerItem = {"preset": True, "name": "stabilized tracker", "description": "track an object with Ashish's trcker", "file": "utils/transformers/presets/preset_stabilizedTrack.txt"}
subtractModeItem = {"preset": True, "name": "subtract mode", "description": "subtract the mode from the image series", "file": "utils/transformers/presets/preset_subtractMode.txt"}
fabienTrackerItem = {"preset": True, "name": "Fabien's tracker", "description": "track an object with Fabien's trcker", "file": "utils/transformers/presets/preset_ourTracker.txt"}
fabienTrackerBboxFixedItem = {"preset": True, "name": "Fabien's tracker (bbox fixed)", "description": "track an object with Fabien's trcker with bbox fixed at the initial position", "file": "utils/transformers/presets/preset_ourTrackerBboxFixed.txt"}
raftItem = {"preset": True, "name": "RAFT", "description": "compute optical flow via RAFT", "file": "utils/transformers/presets/preset_raft.txt"}
pwcnetItem = {"preset": True, "name": "PWC-NET", "description": "compute optical flow via PWC-NET", "file": "utils/transformers/presets/preset_pwcnet.txt"}

presets = \
{
    toGreyscaleItem['name']: toGreyscaleItem,
    subtractModeItem['name']: subtractModeItem,
    "track": \
    {
        "Ashish": \
            {
                stabilizedTrackerItem['name']: stabilizedTrackerItem
            },
        "Fabien": \
            {
                fabienTrackerItem['name']: fabienTrackerItem,
                fabienTrackerBboxFixedItem['name']: fabienTrackerBboxFixedItem
            }
    },
    "optical flow": \
    {
        raftItem['name']: raftItem,
        pwcnetItem['name']: pwcnetItem
    }
}