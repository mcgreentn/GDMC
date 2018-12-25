"""
A set of utility functions used to help connect the partition_tools VoxelPartition class and
partition_utilities functions with the MCEdit API and filter interface.
"""

from partition_tools import *


def get_box_shape(box):
    """
    Code adapted from utilityFunctions.py getBoxSize() function; it is basically the same but
    without the () around the return

    :param box: the level box
    :return: the shape of the level box
    """
    return box.maxx - box.minx, box.maxy - box.miny, box.maxz - box.minz


def box_to_level_index(box, index):
    """
    Transforms an index's local coordinates within a specified box to the global coordiniates
    within the Minecraft level

    :param box: the level box
    :param index: the local box's index
    :return: the global level's index
    """
    return index[0] + box.minx, index[1] + box.miny, index[2] + box.minz


def minecraft_box_to_partition(box):
    """
    Creates an NDVoxelPartition from a given Minecraft level and box. All of the elements of
    the resulting partition are initialized to the 0th partition. That is, creates an initial
    trivial partition from a specified Minecraft level and box.

    :param level: the MCEdit level
    :param box: the MCEdit box
    :return: a VoxelPartition representing an initial trivial partitioning of the specified
    Minecraft level and box.
    """

    element_array = np.full(get_box_shape(box), 0)
    element_indices = []

    for index, element in np.ndenumerate(element_array):
        element_indices.append(index)

    partition = VoxelPartition(element_array, element_indices)

    return partition


def partition_to_minecraft(level, box, voxel_partition, index_offset=0):
    """
    Transforms the contents of a VoxelPartition back into the Minecraft space. Uses
    box_to_level_index to transform the local numpy indices stored in a VoxelPartition
    back into the global Minecraft space indices. If the dimension of the VoxelPartition
    is not 3, returns prematurely.

    :param level: the MCEdit level
    :param box: the MCEdit box
    :param voxel_partition: a VoxelPartition representing a partitioning of the specified
    Minecraft level and box
    :return:
    """

    dimension = len(voxel_partition.shape)
    if dimension is not 3:
        print "Invalid partition dimension,", dimension, "expected 3"
        return

    for index, element_index in voxel_partition.generator():
        level_index = box_to_level_index(box, element_index)

        level.setBlockAt(level_index[0], level_index[1], level_index[2], index + index_offset)


def oct_partition(voxel_partition):
    """
    Given a voxel_partition, uses its bounds to create a quad-space sub-partitioning.

    :param voxel_partition: a given VoxelPartition
    :return:
    """
    cell_centers = subdivide_bounds_3d(voxel_partition.bounds[0], voxel_partition.bounds[1], 2)
    voxel_partition.partition(voronoi_partition, euclidean_metric, cell_centers)