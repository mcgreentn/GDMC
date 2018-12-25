"""
Demo filter using level_utilities and partition_tools. Given a selected box, recursively performs
an oct_partition twice. As of right now, the Method and Metric inputs have no effect on the
filter's performance.
"""

from partition.level_utilities import *
from partition.partition_tools import *

displayName = "Rastopch Filter"

inputs = (
    ("Method", ("Empty", "Voronoi", "Rectangular")),
    ("Metric", ("Euclidean", "Taxicab")),
    ("Param", 0)
)

methods = {
    "Voronoi": voronoi_partition
}


def perform(level, box, options):

    # get MCEdit inputs
    method_name = options["Method"]
    metric_name = options["Metric"]
    param = options["Param"]

    # read from minecraft
    my_partition = minecraft_box_to_partition(box)
    print my_partition.parts

    # initial oct_partition
    oct_partition(my_partition)
    print my_partition.parts

    # two recursive calls to oct_partition
    oct_partition(my_partition.parts[param])
    oct_partition(my_partition.parts[param].parts[param])

    # write to Minecraft
    partition_to_minecraft(level, box, my_partition)
    partition_to_minecraft(level, box, my_partition.parts[param], 9)
    partition_to_minecraft(level, box, my_partition.parts[param].parts[param], 18)

    print "Finished!"