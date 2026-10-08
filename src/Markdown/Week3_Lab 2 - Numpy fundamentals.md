Lab 2 - Numpy fundamentals
CSIT375 AI for Cybersecurity
March 11, 2023
1 Lab Objectives
This lab aims to quickly walk you through the most fundamental parts of NumPy, including:
1. how to create/initiate 1D arrays and 2D matrices,
2. how to get/set the shape of numpy arrays,
3. and basic operations such as how to calculate the dot product of two NumPy arrays, and
take the norms.
Please try out the following cells and run the python code in your notebook.
This is created by cherry-picking from the official documents of NumPy
(https://numpy.org/doc/stable/user/index.html#user). Please refer to the link for more in-
formation.
This is not an assignment and you do not need to submit it
2 Array Creation
2.1 ndarray in NumPy
NumPy’s main object is the homogeneous multidimensional array (ndarray). It is a table of
elements (usually numbers), all of the same type, indexed by a tuple of positive integers.
A list of elements can be expressed as an ndarray of rank 1, i.e. a 1D array; a matrix can be
expressed as an ndarray of rank 2.
Here lists some important attributes of ndarray:
• ndarray.ndim: the rank of the ndarray. For instance, a matrix has a rank of 2.
• ndarray.shape: the dimensions of the ndarray as a tuple of integers. For a matrix having
20 rows and 30 columns, the shape is (20, 30).
• ndarray.size: the total number of elements in the ndarray, which is equal to the product
of the dimensions.
• ndarray.dtype: an object describing the type of the elements in the array.
[1]: import numpy as np
[2]: =
1

arr [1 2 3 4 5 6 7 8 9]
arr.ndim 1
arr.shape (9,)
arr.size 9
arr.dtype int64
There are several ways to create ndarrays.
2.2 Using the array function
You can create a 1D ndarray from an existing list/array easily using the array function.
[3]:
[3] : array([1, 2, 3, 4])
Note that there is only one argument. So never do this:
[4] :
To create a matrix, call array on a sequence of sequence.
[5] : x =
[5] : array([[1, 2],
[3, 4],
[5, 6]])
[6] :
[6]: (3, 2)
2.3 Using zeros, ones, empty
When the contents of the array to be created are unknown, but its dimensions are known, use one
of zeros, ones, empty.
[7] :
[7] : array([[0., 0., 0.],
[0., 0., 0.]])
2

[8] :
[8]: array([[1., 1., 1.],
[1., 1., 1.]])
[9]:
[9]: array([[1., 1., 1.],
[1., 1., 1.]])
The default dtype is numpy.float64 for these functions.
2.4 Using arange, linspace
Similar to range in Python, arange in NumPy returns a sequence of numbers in a ndarray. Use
the dtype parameter to change the type, or use astype() function to cast into another type.
[10]: np.arange(1, 3, 0.2)
[10]: array([1. , 1.2, 1.4, 1.6, 1.8, 2. , 2.2, 2.4, 2.6, 2.8])
Due to the finite precision of floating point numbers, however, it’s better to use linspace when we
are trying to create a sequence of floating point numbers, specifying how many elements we want,
instead of the step.
[11]:
[11]: array([1. , 1.33333333, 1.66666667, 2. , 2.33333333,
2.66666667, 3. ])
3 Playing with the Shapes of ndarrays
[12]: =
[12] : array([1, 2, 3, 4, 5, 6, 7, 8, 9])
3.1 How to Get the Shape of an ndarray
[13] :
[13]: (9,)
3

3.2 How to Reshape the ndarray:
[14] :
[14]: array([[1, 2, 3],
[4, 5, 6],
[7, 8, 9]])
The reshape function returns a new ndarray with the shape changed without modifying the
original one.
[15] :
[15]: array([1, 2, 3, 4, 5, 6, 7, 8, 9])
[16]:
[16]: array([[1],
[2],
[3],
[4],
[5],
[6],
[7],
[8],
[9] ])
To directly modify the shape of an ndarray:
[17]: =
[17]: array([[1, 2, 3],
[4, 5, 6],
[7, 8, 9]])
Note that 1d arrays and 2d arrays are different.
[18]: xx = arr.reshape((1,9))
xx
[18] : array([[1, 2, 3, 4, 5, 6, 7, 8, 9]])
[19] : xx.shape
[19]: (1, 9)
[20] :
4

[20] : array([1, 2, 3, 4, 5, 6, 7, 8, 9])
| [21] :    |     |     |
| --------- | --- | --- |
[21] : array([[1, 2, 3],
[4, 5, 6],
[7, 8, 9]])
[22] :
|     |     |     |
| --- | --- | --- |
[22]: (3, 3)

| 4  Basic Operations  |     |     |
| -------------------- | --- | --- |

| 4.1  | Indexing and slicing  |     |
| ---- | --------------------- | --- |

The items of an array can be accessed and assigned to the same way as other Python sequences
(e.g. lists):

[23] :  a = np.arange(10)
  print(a)

[0 1 2 3 4 5 6 7 8 9]
[23]: (0, 2, 9)
The usual python idiom for reversing a sequence is supported:
| [24] :  |     |     |
| ------- | --- | --- |
[24] : array([9, 8, 7, 6, 5, 4, 3, 2, 1, 0])
For multidimensional arrays, indices are tuples of integers:
[25] :  a = np.diag(np.arange(3))
  print(a)
print(a[1, 1])

a[2, 1] = 10 # third line, second column
  print(a)
print(a[1])

| [[0  0 0]  |        |     |
| ---------- | ------ | --- |
| [0  1 0]   |        |     |
| [0  0 2]]  |        |     |
| 1          |        |     |
| [[ 0       | 0  0]  |     |
  5

[ 0 1 0]
[ 0 10 2]]
[0 1 0]
Slicing: Arrays, like other Python sequences can also be sliced:
[26] : a = np.arange(10)
print(a)
[0 1 2 3 4 5 6 7 8 9]
[2 5 8]
Note that the last index is not included:
[27] :
[27] : array([0, 1, 2, 3])
A small illustrated summary of NumPy indexing and slicing:
[28] :
display(Image(filename="numpy_indexing.png", height=400, width=400))
4.2 Arithmetic Operators
Arithmetic operators on ndarrays apply elementwise (so the operation is vectorized). A new
ndarray will be created to hold the result.
[29] : =
[29] : array([1, 2])
6

[30] : arr + 1
[30] : array([2, 3])
[31] :
[31] : array([2, 4])
[32] :
[32] : array([1, 4])
4.3 Dot Products
Given two ndarrays with proper shapes:
[33] : =
[33]: array([1, 2])
[34]: b =
b
[34]: array([[1],
[2]])
To calculate the dot product, the sentence in the following cell is intuitive but WRONG:
[35]:
[35]: array([[1, 2],
[2, 4]])
To correctly calculate the dot products of two ndarrays, use numpy.dot or the dot function on the
ndarray object.
[36]:
[36]: array([5])
[37]:
[37] : array([5])
Both ways create a new ndarray to hold the results without modifying the original ones.
7

4.4 Norms
See https://docs.scipy.org/doc/numpy/reference/generated/numpy.linalg.norm.html for more de-
tails.
[38] : a = np.arange(3) - 1
print(a)
[-1 0 1]
[39] :
[39]: 1.4142135623730951
[40] :
[40]: 2.0
[41] :
[41]: 1.0
4.5 Matrix multiplication
Since Python 3.5, we can use the operator * for element-wise multiplication, and the operator @
for matrix multiplication.
[42] : A = np.array([[1,2],[3,4]])
B =
@ A B numpy
@
[[3 3]
[5 7]]
[[3 3]
[5 7]]
[[-1 2]
[ 6 4]]
[[2 2]
[5 8]]
[43] : =
@
8

[[ 5]
[11]]
To solve Az = B, we have z = A−1B
[44] : z = np.linalg.inv(A) @ B
z
[44]: array([[ 4. , -1. ],
[-2.5, 1. ]])
[45]:
[45]: array([[-1., 1.],
[ 2., 1.]])
4.6 Working with mathematical formulas
The ease of implementing mathematical formulas that work on arrays is one of the things that
make NumPy so widely used in the scientific Python community.
For example, this is the mean square error formula: 𝑀𝑒𝑎𝑛𝑆𝑞𝑢𝑎𝑟𝑒𝐸𝑟𝑟𝑜𝑟 = 2 1 𝑛 ∑ 𝑛 𝑖= 1 ( 𝑦 𝑖 ′ − 𝑦 𝑖 )2
Implementing this formula is simple and straightforward in NumPy using np.sum and np.square.
Now put what you’ve learned into practice by using numpy to calculate the MSE and type in your
code below.
[ ]:
5 References
NumPy documents: https://numpy.org/doc/stable/user/index.html#user
9



---
## Extracted Text from Embedded Images (OCR)

### OCR Text from PDF Page 6, Image 1 (Image57.png)

>>> a[0, 3:5]
array([3, 4])

>>> al4:, 4:]
array([[44, 55],
(54, 55]])

>>> a[:, 2]
a([2, 12, 22, 32, 42, 52])

>>> a[2::2, ::2]
array([[20, 22, 24],
[40, 42, 44]])

### OCR Text from PDF Page 8, Image 1 (Image66.png)

bE a= Ge) @ bl ED) =f