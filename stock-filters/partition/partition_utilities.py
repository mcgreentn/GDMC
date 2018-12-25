"""
A set of utility functions used in partition_tools and level_utilities
"""

import math
import random


def euclidean_metric(point1, point2):
    """
    The euclidean distance between point1 and point2. If point1 and point2 have
    different dimension, returns 0

    :param point1: an n-dimensional point
    :param point2: an n-dimensional point
    :return: the euclidean distance between point1 and point2
    """

    if len(point1) != len(point2):
        return 0

    dist = 0
    for i in range(len(point1)):
        dxi = point2[i] - point1[i]
        dist = dist + dxi * dxi

    return math.sqrt(dist)


def voronoi_partition(point, metric, cell_centers):
    """
    Returns the corresponding voronoi partition index for the given points. If cell_centers is a
    list of length less than one, returns -1.

    :param point: an n-dimensional point
    :param metric: a distance metric
    :param cell_centers: the voronoi cell centers
    :return: the corresponding voronoi partition index
    """

    if len(cell_centers) < 1:
        return -1

    dist = metric

    partition_index = 0
    min_dist = dist(point, cell_centers[0])

    for i in range(1, len(cell_centers)):
        center = cell_centers[i]
        distance = dist(point, center)

        if distance < min_dist:
            min_dist = distance
            partition_index = i

    return partition_index


def random_indices(shape, amount):
    """
    Given an the shape of a numpy array, returns a specified amount of in-bounds random array
    indices

    :param shape: the shape of an array
    :param amount: the amount of indices to generate
    :return: the list of random indices
    """
    indices = []
    for i in range(amount):
        index = ()
        for j in range(len(shape)):
            index += (random.randint(0, shape[j] - 1)),
        indices.append(index)

    return indices


def voxel_bounds(element_indices):
    """
    Returns a tuple containing the minimum and maximum corners of a bounding box containing
    the element_indices

    This was a very quickly done brute force approach to computing the bounds of a list of
    voxel element indices. How can this be improved?

    :param element_indices: a list of voxel element indices
    :return:
    """
    components = []
    for i in range(len(element_indices[0])):
        components.append([])

    for element_index in element_indices:
        for i in range(len(element_index)):
            components[i].append(element_index[i])

    for component in components:
        component.sort()

    minim = []
    maxim = []
    for component in components:
        minim.append(component[0])
        maxim.append(component[-1])

    return minim, maxim


def in_bounds(index, min, max):
    """
    Returns whether or not a given element is within the bounds of a bounding box specified by
    a minimum and a maximum point

    :param index: a given element index
    :param min: the minimum point of a bounding box
    :param max: the maximum point of a bounding box
    :return: whether or not the given element index is within the bounding box
    """
    for i in range(len(index)):
        if index[i] < min[i] or index[i] > max[i]:
            return False
    return True


def subdivide_bounds_3d(minim, maxim, div):
    """
    Returns a list of points "subdividing" the given 3D bounds div times

    :param minim: the minimum point of a bounding box
    :param maxim: the maximum point of a bounding box
    :param div: the number of subdivisions to perform
    :return: a list of the points "subdividing" the given 3D bounds
    """
    points = []
    for i in range(1, div+1):
        for j in range(1, div+1):
            for k in range(1, div+1):
                x = float(maxim[0] - minim[0]) / (div+1) * i + minim[0]
                y = float(maxim[1] - minim[1]) / (div+1) * j + minim[1]
                z = float(maxim[2] - minim[2]) / (div+1) * k + minim[2]
                points.append((x, y, z))

    return points


def subdivide_bounds_2d(minim, maxim, div):
    """
    Returns a list of points "subdividing" the given 2D bounds div times

    :param minim: the minimum point of a bounding box
    :param maxim: the maximum point of a bounding box
    :param div: the number of subdivisions to perform
    :return: a list of the points "subdividing" the given 2D bounds
    """
    points = []
    for i in range(1, div+1):
        for j in range(1, div+1):
            x = float(maxim[0] - minim[0]) / (div+1) * i + minim[0]
            y = float(maxim[1] - minim[1]) / (div+1) * j + minim[1]
            points.append((x, y))

    return points


if __name__ == "__main__":
    """
    Here, we use some visualizations to test some of the functions defined here. I need to
    add documentation about what is going on here as well as some actual proper testing.
    """

    my_list = random_indices((10, 10), 4)
    my_bounds = voxel_bounds(my_list)
    print my_bounds

    for x in range(10):
        for y in range(10):
            if (x, y) in my_list:
                print '@',
            elif in_bounds((x, y), *my_bounds):
                print '$',
            else:
                print '-',
        print

    sub = subdivide_bounds_2d(my_bounds[0], my_bounds[1], 2)
    print sub

    sub_bounds = []
    for point in sub:
        new_point = []
        for i in range(len(point)):
            new_point.append(int(point[i]))
        sub_bounds.append(tuple(new_point))

    print sub_bounds

    for x in range(10):
        for y in range(10):
            if (x, y) in sub_bounds:
                print '&',
            elif in_bounds((x, y), *my_bounds):
                print '$',
            else:
                print '-',
        print
