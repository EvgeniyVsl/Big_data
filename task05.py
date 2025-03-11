"""
Given a list of integers numbers "nums".

You need to find a sub-array with length less equal to "k", with maximal sum.

The written function should return the sum of this sub-array.

Examples:
    nums = [1, 3, -1, -3, 5, 3, 6, 7], k = 3
    result = 16
"""

nums = [1, 3, -1, -3, 5, 3, 6, 7]
k = 3

def max_subarray_sum(nums:list, k:str):

    # список для подмассивов
    list_of_arrays = []
    # счётчик для сдвига
    counter = 0

    # проходимся по всем элементам массива
    for i in range(len(nums)):
        single_array = []
        try:
            # добавляем в один подмассив столько значений, сколько определено в k
            for i in range(k):
                i = i + counter
                single_array.append(nums[i])     
            # после добавления подмассива в список сдвигаемся на одно значение
            counter += 1
            list_of_arrays.append(single_array) 
        except:
            # Доходя до конца списка, код начинает выдавать ошибку из-за index out of range. Мы уже заполнили список всеми нужными значениями, поэтому можно просто выпасть из цикла
            # Способ не самый красивый, но работает :)
            break
        
        summs = []
        # проходимся по всем подмассивам и считаем их суммы, в конце выводим максимум
        for sub_array in list_of_arrays:
            summ_value = 0
            for i in sub_array:
                summ_value+=i
            summs.append(summ_value)
    
    return max(summs)

print(max_subarray_sum(nums,k))
