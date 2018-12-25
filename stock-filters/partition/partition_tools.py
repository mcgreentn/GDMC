"""
A definition of the VoxelPartition class as well as basic testing of said class in
the main method.
"""

import numpy as np
from partition_utilities import *


class VoxelPartition:
    """
    A VoxelPartition represents a partitioning of a set of voxels. When partitioned,
    a VoxelPartition represents each of its sub-partitions in a resulting tree structure.

    A VoxelPartition's set of voxels is implicitly represented by a numpy array. In this
    numpy array, each index corresponds to a given voxel's center in n-dimensional space,
    and each value corresponds to a given voxel's partition index. For example, a
    VoxelPartition will represent a partitioning where every element belongs to the same
    part, or a trivial partitioning, as a collection of indices each of which belongs to
    the 0th part of the partitioning. Internally, the VoxelPartition class keeps track of
    this information with three members:

        element_array is a reference to the numpy array representing the superset of all
        possible voxel. Each index corresponds to a given voxel's center in n-dimensional
        space, and each value corresponds to a given voxel's partition index.

        element_indices is a list of the subset of indices from element_array composing
        the elements in a given VoxelPartition. Whereas element_array represents the
        superset of all possible voxels, element)indices keeps track of the set of voxels
        that correspond to a given VoxelPartition. We keep track of this list of indices
        so that we can build our resulting partition tree structure.

        parts is a dictionary (map) of (partition index, sub-partition) pairs. We use this
        to represent the sub-partitions of a given VoxelPartition.

    We create and manipulate VoxelPartitions as follows. First, the VoxelPartition
    constructor, when only given one parameter, namely, a reference to the superset of
    all voxels, element_array, creates a VoxelPartition representing the above described
    trivial partition. Such a trivial VoxelPartition will copy each index from the initial
    numpy array into its element_indices list, as well as have parts initialized to an
    empty dictionary. When the parts member is the empty dictionary, we know that every
    index in the element_indices list is an element of the current partition, and thusly
    we know we are in an empty partitioning. When we create sub-partitions of a given
    VoxelPartition, each sub-partition is also initialized as a trivial partition,
    however, instead of using all of the element_array indices, it is initialized with a
    subset of the element_array indices. When we partition a VoxelPartition, we actually
    partition the element_indices list into disjoint sub-VoxelPartitions. In this fashion,
    the root of our resulting VoxelPartition tree is the first partition containing all
    of the indices from the element_array, and the leaves of our resulting VoxelPartition
    tree are VoxelPartitions with the parts member being empty dictionaries.


    Design Notes

    1) This implementation uses a Python list to keep track of a VoxelPartition's
    element_indices. We do this because we do not know how many elements will appear in a
    resulting sub-partition of a given VoxelPartition. Thusly, the data structure that we
    use to keep track of the element_indices must be dynamically sized, and we cannot use
    a numpy array. This can be problematic when we want to iterate over every element in
    a VoxelPartition, because our list get operations may not be as fast as array accesses.
    When we use this data structure, are we going to be frequently iterating over each of
    elements corresponding to a given VoxelPartition? When partitioning a given partition,
    are we going to be appending to the end of our list frequently? These are two questions
    that might guide us in determining whether or not a Python list is the appropriate
    data structure for representing the set of element_indices.

    One approach that might mitigate the Python list access runtime is to represent the
    element_indices with some sort of ArrayList data structure. A quick search online
    revealed implementations of the ArrayList data structure using numpy lists as the
    internal array data structure.

    Another way to make our traversal and partitioning more efficient, suggested by
    Professor John D. Stone, is to represent the partition tree not as a tree of lists
    of subsets of indices, but instead as an octree. This requires further research.


    2) This implementation thinks of the numpy array of voxels as being n-dimensional. The
    only function we use that is constrained to 2 or 3 dimensions are the subdivide_bounds
    functions (in partition_utilities). Given that this implementation is designed for use
    on the 3D Minecraft voxel grids, would it simplify the problem to constrain the input to
    # dimensions?

    3) Given two VoxelPartitions, in the future we might want to perform set operations on
    them such as union, intersect, and difference. How might we go about implementing these
    operations? How does this affect design note #1?

    4) How might we use Scipy to simplify and make more efficient our code? Scipy has a spatial
    library that already has fast implementations of all sorts of different metrics, space
    partitioning algorithms (it has an n-dimensional voronoi function), as well as data structures
    (it has a kdtree implementation). Can this help us simplify our representation of the
    element_indices set? Can this give us a way of computing the bounds of a VoxelPartition
    that is not a brute-force algorithm?

    5) In terms of translating a VoxelPartition back to the Minecraft world, the partition to
    Minecraft function only does this for the elements of a given VoxelPartition. Instead, we
    should implement some sort of tree traversal that efficiently iterates through the
    VoxelPartition tree structure. This would lead to more efficient and cleaner code and get
    rid of the three calls to partition_to_minecraft in rastopch_filter.

    """

    def __init__(self, element_array, element_indices=None):
        """
        VoxelPartition constructor

        When element_indices is unspecified, creates a VoxelPartition containing an initial
        trivial partitioning of the element_array.

        When element_indices is specified, creates a VoxelPartition containing a trivial
        partitioning with the specified subset of element indices.

        :param element_array: reference to superset of all possible voxels
        :param element_indices: index list of set of voxels to be partitioned
        """

        self.element_array = element_array  # reference of voxel superset
        self.element_indices = element_indices  # reference to list of element indices
        self.parts = {}  # initialize map of (part_index, sub-partition) pairs

        self.shape = element_array.shape  # array shape
        self.bounds = ((0, 0, 0), self.shape)  # initial element bounds

        # If element_indices unspecified, create root trivial partition
        if element_indices is None:
            self.element_indices = []
            for index, element in np.ndenumerate(element_array):
                self.element_indices.append(index)

            # recalculate partition bounds
            self.bounds = voxel_bounds(self.element_indices)

    def partition(self, method, *args):
        """
        Partitions the VoxelPartition based on a given partitioning method.

        Design Notes:

        1) Perhaps instead of recalculating the bounds of a VoxelPartition when
        updating the voxel bounds directly after the partitioning, we could
        determine these new bounds while producing our new partitionin?

        2) If we call the partition method on a non-leaf of our VoxelPartition
        tree structure, what happens? Are all of our children VoxelPartition's
        appropriately managed?

        :param method: a partitioning method (i.e. voronoi_partition, etc.)
        :param args: additional arguments for the specified partitioning method
        :return:
        """
        # reset parts map
        self.parts = {}

        # create initial partition
        for element_index in self.element_indices:

            # compute index of element in new partitioning
            new_part_index = method(element_index, *args)

            # if this part does not yet exist, create it
            if new_part_index not in self.parts:
                new_element_indices = [element_index]
                new_part = VoxelPartition(self.element_array, new_element_indices)
                self.parts[new_part_index] = new_part
            # if it does already exist, add this index to element_indices in the corresponding part
            else:
                part = self.parts[new_part_index]
                part.element_indices.append(element_index)

        # for each sub-partition, update partition voxel bounds
        for sub_partition in self.parts.values():
            sub_partition.update_voxel_bounds()

    def parts_gen(self):
        """
        A generator yielding (partition index (int), sub-partition (VoxelPartition)) pairs

        :return: a generator yielding (partition index, sub-partition) pairs
        """

        for part_index, sub_partition in self.parts.iteritems():
            yield (part_index, sub_partition)

    def generator(self):
        """
        A generator yielding each (partition index (int), element index (tuple)) pair stored in the
        VoxelPartition.

        :return: a generator yielding (each part_index, element_index) pair stored in the
        VoxelPartition
        """
        for part_index, sub_partition in self.parts_gen():
            for element_index in sub_partition.element_indices:
                yield(part_index, element_index)

    def update_voxel_bounds(self):
        """
        Updates the bounds member by using the brute-force voxel_bounds helper function
        :return:
        """
        self.bounds = voxel_bounds(self.element_indices)

    def __str__(self):
        """
        Returns an interpretable visualization of a VoxelPartition when working with a 2D
        numpy element_array. If the dimension of the element_array is not 2, returns the
        empty String.

        The __str__ method takes advantage of the numpy __str__ method, representing the
        contents of a partition by copying each element and its corresponding partition index
        into a new numpy array. Visually, each element in the resulting printed numpy array
        will correspond to that element's partition index plus 1. Thusly, an initialized and
        un-partitioned VoxelPartition should look like a matrix of 1s. After a partitioning, a
        VoxelPartition should be filled with different numbers. When we print each sub partition,
        we represent them a little bit differently. A sub-partition will consist of 0s, 1s,
        and 2s. 1s represent elements in that particular sub-partition, 2s represent elements
        within the bounding-box of that sub-partition, and 0s represent elements in the super-set
        the partition belongs to but disjoint from the actual partition and its bounding box.

        :return: an interpretable visualization of the contents of a 2D VoxelPartition
        """

        # if dimension of the element_array is not 2, return empty String
        if len(self.shape) != 2:
            return ""

        # create a copy of the superset element_array
        elements_copy = np.copy(self.element_array)

        # if leaf VoxelPartition, visualize corresponding elements and bounds
        if not self.parts:
            for element_index, element in np.ndenumerate(self.element_array):
                # if an element
                if element_index in self.element_indices:
                    elements_copy[element_index] = 1
                # if not an element but in bounding box
                elif in_bounds(element_index, self.bounds[0], self.bounds[1]):
                    elements_copy[element_index] = 2

        # if non-leaf VoxelPartition, visualize all of the sub-parts
        else:
            for part_index, element_index in self.generator():
                elements_copy[element_index] = part_index + 1

        return elements_copy.__str__()


if __name__ == "__main__":
    """
    Here, we use the __str__ method of the VoxelPartition class to visually inspect
    and test recursive partitioning of 20 x 20 0-initialized numpy array. We perform
    basic testing.
    
    Here, we use the VoxelPartition __str__ method to visually inspect and test the
    VoxelPartition class and adjacent functions. See the docstring of the
    VoxelPartition.__str__(self) to interpret the results printed to the console.
    """

    print "\nPRIMARY TESTING: RANDOM VORONOI\n"

    def print_partition(partition):
        """
        Partition testing printing helper function

        :param partition: a VoxelPartition
        :return:
        """
        print "Shape:", partition.shape, "Bounds:", partition.bounds
        print "Parts: {",
        for part_index, part in partition.parts_gen():
            print "{0}: elements: {1}".format(part_index, len(part.element_indices)),
        print "}\n"

        print partition, "\n"

    print "\tInitial trivial partition of a 20 x 20 0-initialized numpy array:\n"
    element_array = np.full((20, 20), 0)
    my_partition = VoxelPartition(element_array, None)
    print_partition(my_partition)

    print "\tPost random-cell-center voronoi partition:\n"
    my_partition.partition(voronoi_partition, euclidean_metric, random_indices(my_partition.shape, 4))
    print_partition(my_partition)

    print "\tEach sub-partition:\n"
    for part_index, partition in my_partition.parts_gen():
        print_partition(partition)

    print "\tFirst sub-partition:\n"
    first_part = my_partition.parts[0]
    print_partition(first_part)

    print "\tPerforming a quad-space partitioning of the first sub-partition:\n"
    cell_centers = subdivide_bounds_2d(first_part.bounds[0], first_part.bounds[1], 2)
    first_part.partition(voronoi_partition, euclidean_metric, cell_centers)
    print_partition(first_part)

    print "\nSECONDARY TESTING: PRIMARY AND SECONDARY QUAD-SPACE PARTITIONING\n"

    print "\tInitial trivial partition of a 20 x 20 0-initialized numpy array:\n"
    element_array = np.full((20, 20), 0)
    my_partition = VoxelPartition(element_array, None)
    print_partition(my_partition)

    print "\tInitial quad-space partitioning:\n"
    quad_div = subdivide_bounds_2d(my_partition.bounds[0], my_partition.bounds[1], 2)
    my_partition.partition(voronoi_partition, euclidean_metric, quad_div)
    print_partition(my_partition)

    print "\tFirst part produced by the initial quad-space partitioning:\n"
    first_part = my_partition.parts[0]
    print_partition(first_part)

    print "\tSecondary quad-space partitioning:\n"
    quad_div = subdivide_bounds_2d(first_part.bounds[0], first_part.bounds[1], 2)
    first_part.partition(voronoi_partition, euclidean_metric, quad_div)
    print_partition(first_part)

    print "END OF INITIAL TESTING"
