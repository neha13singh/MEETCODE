import asyncio
import logging
import sys
import os
import uuid

# Ensure app can be imported
sys.path.append(os.getcwd())

from sqlalchemy import select, text
from app.db.session import engine, AsyncSessionLocal
from app.models.question import Question, TestCase, CodeTemplate
from app.models.match import Match, MatchParticipant
from app.models.user import User

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

QUESTIONS_DATA = [
    # EASY QUESTIONS
    {
        "title": "Two Sum",
        "slug": "two-sum",
        "difficulty": "easy",
        "description": "Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.",
        "avg_solve_time": 600,
        "examples": [
            {"input": "nums = [2,7,11,15], target = 9", "output": "[0,1]"},
            {"input": "nums = [3,2,4], target = 6", "output": "[1,2]"}
        ],
        "test_cases": [
            {"input": "nums = [2,7,11,15], target = 9", "expected_output": "[0,1]", "is_sample": True},
            {"input": "nums = [3,2,4], target = 6", "expected_output": "[1,2]", "is_sample": True},
            {"input": "nums = [3,3], target = 6", "expected_output": "[0,1]", "is_sample": True},
            {"input": "nums = [1,2,3,4], target = 7", "expected_output": "[2,3]", "is_hidden": True},
            {"input": "nums = [0,4,3,0], target = 0", "expected_output": "[0,3]", "is_hidden": True}
        ],
        "template": "class Solution:\n    def twoSum(self, nums: List[int], target: int) -> List[int]:\n        pass"
    },
    {
        "title": "Palindrome Number",
        "slug": "palindrome-number",
        "difficulty": "easy",
        "description": "Given an integer x, return true if x is a palindrome, and false otherwise.",
        "avg_solve_time": 300,
        "examples": [
            {"input": "x = 121", "output": "true"},
            {"input": "x = -121", "output": "false"}
        ],
        "test_cases": [
            {"input": "x = 121", "expected_output": "True", "is_sample": True},
            {"input": "x = -121", "expected_output": "False", "is_sample": True},
            {"input": "x = 10", "expected_output": "False", "is_sample": True},
            {"input": "x = 12321", "expected_output": "True", "is_hidden": True},
            {"input": "x = 123456", "expected_output": "False", "is_hidden": True}
        ],
        "template": "class Solution:\n    def isPalindrome(self, x: int) -> bool:\n        pass"
    },
    {
        "title": "Roman to Integer",
        "slug": "roman-to-integer",
        "difficulty": "easy",
        "description": "Given a roman numeral, convert it to an integer.",
        "avg_solve_time": 600,
        "examples": [
            {"input": "s = \"III\"", "output": "3"},
            {"input": "s = \"LVIII\"", "output": "58"}
        ],
        "test_cases": [
            {"input": "s = \"III\"", "expected_output": "3", "is_sample": True},
            {"input": "s = \"LVIII\"", "expected_output": "58", "is_sample": True},
            {"input": "s = \"IX\"", "expected_output": "9", "is_sample": True},
            {"input": "s = \"MCMXCIV\"", "expected_output": "1994", "is_hidden": True},
            {"input": "s = \"MMMCMXCIX\"", "expected_output": "3999", "is_hidden": True}
        ],
        "template": "class Solution:\n    def romanToInt(self, s: str) -> int:\n        pass"
    },
    {
        "title": "Valid Parentheses",
        "slug": "valid-parentheses",
        "difficulty": "easy",
        "description": "Given a string s containing just the characters '(', ')', '{', '}', '[' and ']', determine if the input string is valid.",
        "avg_solve_time": 600,
        "examples": [
            {"input": "s = \"()\"", "output": "true"},
            {"input": "s = \"()[]{}\"", "output": "true"}
        ],
        "test_cases": [
            {"input": "s = \"()\"", "expected_output": "True", "is_sample": True},
            {"input": "s = \"()[]{}\"", "expected_output": "True", "is_sample": True},
            {"input": "s = \"(]\"", "expected_output": "False", "is_sample": True},
            {"input": "s = \"([)]\"", "expected_output": "False", "is_hidden": True},
            {"input": "s = \"{[]}\"", "expected_output": "True", "is_hidden": True}
        ],
        "template": "class Solution:\n    def isValid(self, s: str) -> bool:\n        pass"
    },
    {
        "title": "Remove Duplicates from Sorted Array",
        "slug": "remove-duplicates",
        "difficulty": "easy",
        "description": "Given an integer array nums sorted in non-decreasing order, remove the duplicates in-place such that each unique element appears only once. Return number of unique elements.",
        "avg_solve_time": 600,
        "examples": [
            {"input": "nums = [1,1,2]", "output": "2"},
            {"input": "nums = [0,0,1,1,1,2,2,3,3,4]", "output": "5"}
        ],
        "test_cases": [
            {"input": "nums = [1,1,2]", "expected_output": "2", "is_sample": True},
            {"input": "nums = [0,0,1,1,1,2,2,3,3,4]", "expected_output": "5", "is_sample": True},
            {"input": "nums = [1,2,3]", "expected_output": "3", "is_sample": True},
            {"input": "nums = [1,1,1,1,1]", "expected_output": "1", "is_hidden": True},
            {"input": "nums = [-1,0,0,3,3]", "expected_output": "3", "is_hidden": True}
        ],
        "template": "class Solution:\n    def removeDuplicates(self, nums: List[int]) -> int:\n        pass"
    },
    {
        "title": "Plus One",
        "slug": "plus-one",
        "difficulty": "easy",
        "description": "You are given a large integer represented as an integer array digits. Increment the large integer by one and return the resulting array of digits.",
        "avg_solve_time": 400,
        "examples": [
            {"input": "digits = [1,2,3]", "output": "[1,2,4]"},
            {"input": "digits = [9]", "output": "[1,0]"}
        ],
        "test_cases": [
            {"input": "digits = [1,2,3]", "expected_output": "[1,2,4]", "is_sample": True},
            {"input": "digits = [9]", "expected_output": "[1,0]", "is_sample": True},
            {"input": "digits = [4,3,2,1]", "expected_output": "[4,3,2,2]", "is_sample": True},
            {"input": "digits = [9,9,9]", "expected_output": "[1,0,0,0]", "is_hidden": True},
            {"input": "digits = [0]", "expected_output": "[1]", "is_hidden": True}
        ],
        "template": "class Solution:\n    def plusOne(self, digits: List[int]) -> List[int]:\n        pass"
    },
    {
        "title": "Climbing Stairs",
        "slug": "climbing-stairs",
        "difficulty": "easy",
        "description": "You are climbing a staircase. It takes n steps to reach the top. Each time you can either climb 1 or 2 steps. In how many distinct ways can you climb to the top?",
        "avg_solve_time": 500,
        "examples": [
            {"input": "n = 2", "output": "2"},
            {"input": "n = 3", "output": "3"}
        ],
        "test_cases": [
            {"input": "n = 2", "expected_output": "2", "is_sample": True},
            {"input": "n = 3", "expected_output": "3", "is_sample": True},
            {"input": "n = 4", "expected_output": "5", "is_sample": True},
            {"input": "n = 5", "expected_output": "8", "is_hidden": True},
            {"input": "n = 10", "expected_output": "89", "is_hidden": True}
        ],
        "template": "class Solution:\n    def climbStairs(self, n: int) -> int:\n        pass"
    },
    {
        "title": "Sqrt(x)",
        "slug": "sqrt-x",
        "difficulty": "easy",
        "description": "Given a non-negative integer x, return the square root of x rounded down to the nearest integer.",
        "avg_solve_time": 600,
        "examples": [
            {"input": "x = 4", "output": "2"},
            {"input": "x = 8", "output": "2"}
        ],
        "test_cases": [
            {"input": "x = 4", "expected_output": "2", "is_sample": True},
            {"input": "x = 8", "expected_output": "2", "is_sample": True},
            {"input": "x = 1", "expected_output": "1", "is_sample": True},
            {"input": "x = 0", "expected_output": "0", "is_hidden": True},
            {"input": "x = 2147395599", "expected_output": "46339", "is_hidden": True}
        ],
        "template": "class Solution:\n    def mySqrt(self, x: int) -> int:\n        pass"
    },
    {
        "title": "Length of Last Word",
        "slug": "length-of-last-word",
        "difficulty": "easy",
        "description": "Given a string s consisting of words and spaces, return the length of the last word in the string.",
        "avg_solve_time": 300,
        "examples": [
            {"input": "s = \"Hello World\"", "output": "5"},
            {"input": "s = \"   fly me   to   the moon  \"", "output": "4"}
        ],
        "test_cases": [
            {"input": "s = \"Hello World\"", "expected_output": "5", "is_sample": True},
            {"input": "s = \"   fly me   to   the moon  \"", "expected_output": "4", "is_sample": True},
            {"input": "s = \"a\"", "expected_output": "1", "is_sample": True},
            {"input": "s = \"luffy is still joyboy\"", "expected_output": "6", "is_hidden": True},
            {"input": "s = \"        \"", "expected_output": "0", "is_hidden": True}
        ],
        "template": "class Solution:\n    def lengthOfLastWord(self, s: str) -> int:\n        pass"
    },
    {
        "title": "Search Insert Position",
        "slug": "search-insert-position",
        "difficulty": "easy",
        "description": "Given a sorted array of distinct integers and a target value, return the index if the target is found. If not, return the index where it would be if it were inserted.",
        "avg_solve_time": 500,
        "examples": [
            {"input": "nums = [1,3,5,6], target = 5", "output": "2"},
            {"input": "nums = [1,3,5,6], target = 2", "output": "1"}
        ],
        "test_cases": [
            {"input": "nums = [1,3,5,6], target = 5", "expected_output": "2", "is_sample": True},
            {"input": "nums = [1,3,5,6], target = 2", "expected_output": "1", "is_sample": True},
            {"input": "nums = [1,3,5,6], target = 0", "expected_output": "0", "is_sample": True},
            {"input": "nums = [1,3,5,6], target = 7", "expected_output": "4", "is_hidden": True},
            {"input": "nums = [1,3,5,6], target = 4", "expected_output": "2", "is_hidden": True}
        ],
        "template": "class Solution:\n    def searchInsert(self, nums: List[int], target: int) -> int:\n        pass"
    },
    # MEDIUM QUESTIONS
    {
        "description": "Given a string containing digits from 2-9 inclusive, return all possible letter combinations that the number could represent. Return the answer in any order.",
        "difficulty": "medium",
        "title": "Letter Combinations of a Phone Number",
        "slug": "letter-combinations",
        "avg_solve_time": 900,
        "examples": [
            {"input": "digits = \"23\"", "output": "[\"ad\",\"ae\",\"af\",\"bd\",\"be\",\"bf\",\"cd\",\"ce\",\"cf\"]"},
            {"input": "digits = \"\"", "output": "[]"}
        ],
        "test_cases": [
            {"input": "digits = \"23\"", "expected_output": "['ad', 'ae', 'af', 'bd', 'be', 'bf', 'cd', 'ce', 'cf']", "is_sample": True},
            {"input": "digits = \"\"", "expected_output": "[]", "is_sample": True},
            {"input": "digits = \"2\"", "expected_output": "['a', 'b', 'c']", "is_sample": True},
            {"input": "digits = \"9\"", "expected_output": "['w', 'x', 'y', 'z']", "is_hidden": True},
            {"input": "digits = \"22\"", "expected_output": "['aa', 'ab', 'ac', 'ba', 'bb', 'bc', 'ca', 'cb', 'cc']", "is_hidden": True}
        ],
        "template": "class Solution:\n    def letterCombinations(self, digits: str) -> List[str]:\n        pass"
    },
    {
        "title": "Add Two Numbers",
        "slug": "add-two-numbers",
        "difficulty": "medium",
        "description": "You are given two non-empty linked lists representing two non-negative integers. The digits are stored in reverse order, and each of their nodes contains a single digit. Add the two numbers and return the sum as a linked list.",
        "avg_solve_time": 900,
        "examples": [
            {"input": "l1 = [2,4,3], l2 = [5,6,4]", "output": "[7,0,8]"},
            {"input": "l1 = [0], l2 = [0]", "output": "[0]"}
        ],
        "test_cases": [
            {"input": "l1 = [2,4,3], l2 = [5,6,4]", "expected_output": "[7,0,8]", "is_sample": True},
            {"input": "l1 = [0], l2 = [0]", "expected_output": "[0]", "is_sample": True},
            {"input": "l1 = [9,9,9], l2 = [1]", "expected_output": "[0,0,0,1]", "is_sample": True},
            {"input": "l1 = [9,9,9,9,9,9,9], l2 = [9,9,9,9]", "expected_output": "[8,9,9,9,0,0,0,1]", "is_hidden": True},
            {"input": "l1 = [2,4,9], l2 = [5,6,4]", "expected_output": "[7,0,4,1]", "is_hidden": True}
        ],
        "template": "class Solution:\n    def addTwoNumbers(self, l1: Optional[ListNode], l2: Optional[ListNode]) -> Optional[ListNode]:\n        pass"
    },
    {
        "title": "Longest Substring Without Repeating Characters",
        "slug": "longest-substring",
        "difficulty": "medium",
        "description": "Given a string s, find the length of the longest substring without repeating characters.",
        "avg_solve_time": 1200,
        "examples": [
            {"input": "s = \"abcabcbb\"", "output": "3"},
            {"input": "s = \"bbbbb\"", "output": "1"}
        ],
        "test_cases": [
            {"input": "s = \"abcabcbb\"", "expected_output": "3", "is_sample": True},
            {"input": "s = \"bbbbb\"", "expected_output": "1", "is_sample": True},
            {"input": "s = \"pwwkew\"", "expected_output": "3", "is_sample": True},
            {"input": "s = \"\"", "expected_output": "0", "is_hidden": True},
            {"input": "s = \"dvdf\"", "expected_output": "3", "is_hidden": True}
        ],
        "template": "class Solution:\n    def lengthOfLongestSubstring(self, s: str) -> int:\n        pass"
    },
    {
        "title": "Container With Most Water",
        "slug": "container-with-most-water",
        "difficulty": "medium",
        "description": "You are given an integer array height of length n. There are n vertical lines drawn such that the two endpoints of the ith line are (i, 0) and (i, height[i]). Find two lines that together with the x-axis form a container, such that the container contains the most water.",
        "avg_solve_time": 900,
        "examples": [
            {"input": "height = [1,8,6,2,5,4,8,3,7]", "output": "49"},
            {"input": "height = [1,1]", "output": "1"}
        ],
        "test_cases": [
            {"input": "height = [1,8,6,2,5,4,8,3,7]", "expected_output": "49", "is_sample": True},
            {"input": "height = [1,1]", "expected_output": "1", "is_sample": True},
            {"input": "height = [4,3,2,1,4]", "expected_output": "16", "is_sample": True},
            {"input": "height = [1,2,1]", "expected_output": "2", "is_hidden": True},
            {"input": "height = [1,8,6,2,5,4,8,25,7]", "expected_output": "49", "is_hidden": True}
        ],
        "template": "class Solution:\n    def maxArea(self, height: List[int]) -> int:\n        pass"
    },
    {
        "title": "3Sum",
        "slug": "3sum",
        "difficulty": "medium",
        "description": "Given an integer array nums, return all the triplets [nums[i], nums[j], nums[k]] such that i != j, i != k, and j != k, and nums[i] + nums[j] + nums[k] == 0.",
        "avg_solve_time": 1200,
        "examples": [
            {"input": "nums = [-1,0,1,2,-1,-4]", "output": "[[-1,-1,2],[-1,0,1]]"},
            {"input": "nums = [0,1,1]", "output": "[]"}
        ],
        "test_cases": [
            {"input": "nums = [-1,0,1,2,-1,-4]", "expected_output": "[[-1,-1,2],[-1,0,1]]", "is_sample": True},
            {"input": "nums = [0,1,1]", "expected_output": "[]", "is_sample": True},
            {"input": "nums = [0,0,0]", "expected_output": "[[0,0,0]]", "is_sample": True},
            {"input": "nums = [-2,0,1,1,2]", "expected_output": "[[-2,0,2],[-2,1,1]]", "is_hidden": True},
            {"input": "nums = [1,2,3]", "expected_output": "[]", "is_hidden": True}
        ],
        "template": "class Solution:\n    def threeSum(self, nums: List[int]) -> List[List[int]]:\n        pass"
    },
    {
        "title": "Generate Parentheses",
        "slug": "generate-parentheses",
        "difficulty": "medium",
        "description": "Given n pairs of parentheses, write a function to generate all combinations of well-formed parentheses.",
        "avg_solve_time": 1000,
        "examples": [
            {"input": "n = 3", "output": "[\"((()))\",\"(()())\",\"(())()\",\"()(())\",\"()()()\"]"},
            {"input": "n = 1", "output": "[\"()\"]"}
        ],
        "test_cases": [
            {"input": "n = 3", "expected_output": "['((()))', '(()())', '(())()', '()(())', '()()()']", "is_sample": True},
            {"input": "n = 1", "expected_output": "['()']", "is_sample": True},
            {"input": "n = 2", "expected_output": "['(())', '()()']", "is_sample": True},
            {"input": "n = 0", "expected_output": "[]", "is_hidden": True},
            {"input": "n = 4", "expected_output": "['(((())))', '((()()))', '((())())', '((()))()', '(()(()))', '(()()())', '(()())()', '(())(())', '(())()()', '()((()))', '()(()())', '()(())()', '()()(())', '()()()()']", "is_hidden": True}
        ],
        "template": "class Solution:\n    def generateParenthesis(self, n: int) -> List[str]:\n        pass"
    },
    {
        "title": "Permutations",
        "slug": "permutations",
        "difficulty": "medium",
        "description": "Given an array nums of distinct integers, return all the possible permutations. You can return the answer in any order.",
        "avg_solve_time": 800,
        "examples": [
            {"input": "nums = [1,2,3]", "output": "[[1,2,3],[1,3,2],[2,1,3],[2,3,1],[3,1,2],[3,2,1]]"},
            {"input": "nums = [0,1]", "output": "[[0,1],[1,0]]"}
        ],
        "test_cases": [
            {"input": "nums = [1,2,3]", "expected_output": "[[1,2,3],[1,3,2],[2,1,3],[2,3,1],[3,1,2],[3,2,1]]", "is_sample": True},
            {"input": "nums = [0,1]", "expected_output": "[[0,1],[1,0]]", "is_sample": True},
            {"input": "nums = [1]", "expected_output": "[[1]]", "is_sample": True},
            {"input": "nums = [1,2]", "expected_output": "[[1,2],[2,1]]", "is_hidden": True},
            {"input": "nums = [0,-1,1]", "expected_output": "[[0,-1,1],[0,1,-1],[-1,0,1],[-1,1,0],[1,0,-1],[1,-1,0]]", "is_hidden": True}
        ],
        "template": "class Solution:\n    def permute(self, nums: List[int]) -> List[List[int]]:\n        pass"
    },
    {
        "title": "Rotate Image",
        "slug": "rotate-image",
        "difficulty": "medium",
        "description": "You are given an n x n 2D matrix representing an image, rotate the image by 90 degrees (clockwise). You have to rotate the image in-place.",
        "avg_solve_time": 1200,
        "examples": [
            {"input": "matrix = [[1,2,3],[4,5,6],[7,8,9]]", "output": "[[7,4,1],[8,5,2],[9,6,3]]"},
             {"input": "matrix = [[5,1,9,11],[2,4,8,10],[13,3,6,7],[15,14,12,16]]", "output": "[[15,13,2,5],[14,3,4,1],[12,6,8,9],[16,7,10,11]]"}
        ],
        "test_cases": [
            {"input": "matrix = [[1,2,3],[4,5,6],[7,8,9]]", "expected_output": "[[7,4,1],[8,5,2],[9,6,3]]", "is_sample": True},
            {"input": "matrix = [[1,2],[3,4]]", "expected_output": "[[3,1],[4,2]]", "is_sample": True},
            {"input": "matrix = [[1]]", "expected_output": "[[1]]", "is_sample": True},
            {"input": "matrix = [[5,1,9,11],[2,4,8,10],[13,3,6,7],[15,14,12,16]]", "expected_output": "[[15,13,2,5], [14,3,4,1], [12,6,8,9], [16,7,10,11]]", "is_hidden": True},
            {"input": "matrix = [[0,0],[0,0]]", "expected_output": "[[0,0],[0,0]]", "is_hidden": True}
        ],
        "template": "class Solution:\n    def rotate(self, matrix: List[List[int]]) -> None:\n        path"
    },
    {
        "title": "Group Anagrams",
        "slug": "group-anagrams",
        "difficulty": "medium",
        "description": "Given an array of strings strs, group the anagrams together. You can return the answer in any order.",
        "avg_solve_time": 800,
        "examples": [
             {"input": "strs = [\"eat\",\"tea\",\"tan\",\"ate\",\"nat\",\"bat\"]", "output": "[[\"bat\"],[\"nat\",\"tan\"],[\"ate\",\"eat\",\"tea\"]]"},
             {"input": "strs = [\"\"]", "output": "[[\"\"]]"}
        ],
        "test_cases": [
             {"input": "strs = [\"eat\",\"tea\",\"tan\",\"ate\",\"nat\",\"bat\"]", "expected_output": "[['eat', 'tea', 'ate'], ['tan', 'nat'], ['bat']]", "is_sample": True},
             {"input": "strs = [\"\"]", "expected_output": "[['']]", "is_sample": True},
             {"input": "strs = [\"a\"]", "expected_output": "[['a']]", "is_sample": True},
             {"input": "strs = [\"ab\",\"ba\",\"abc\",\"cba\",\"bca\"]", "expected_output": "[['ab', 'ba'], ['abc', 'cba', 'bca']]", "is_hidden": True},
             {"input": "strs = [\"listen\",\"silent\",\"hello\",\"world\"]", "expected_output": "[['listen', 'silent'], ['hello'], ['world']]", "is_hidden": True}
        ],
        "template": "class Solution:\n    def groupAnagrams(self, strs: List[str]) -> List[List[str]]:\n        pass"
    },
    {
        "title": "Jump Game",
        "slug": "jump-game",
        "difficulty": "medium",
        "description": "You are given an integer array nums. You are initially positioned at the array's first index. Each element in the array represents your maximum jump length at that position. Return true if you can reach the last index, otherwise return false.",
        "avg_solve_time": 600,
        "examples": [
            {"input": "nums = [2,3,1,1,4]", "output": "true"},
            {"input": "nums = [3,2,1,0,4]", "output": "false"}
        ],
        "test_cases": [
            {"input": "nums = [2,3,1,1,4]", "expected_output": "True", "is_sample": True},
            {"input": "nums = [3,2,1,0,4]", "expected_output": "False", "is_sample": True},
            {"input": "nums = [0]", "expected_output": "True", "is_sample": True},
            {"input": "nums = [1,0,1,0]", "expected_output": "False", "is_hidden": True},
            {"input": "nums = [2,0,0]", "expected_output": "True", "is_hidden": True}
        ],
        "template": "class Solution:\n    def canJump(self, nums: List[int]) -> bool:\n        pass"
    },
    # HARD QUESTIONS
    {
        "title": "Median of Two Sorted Arrays",
        "slug": "median-of-two-sorted-arrays",
        "difficulty": "hard",
        "description": "Given two sorted arrays nums1 and nums2 of size m and n respectively, return the median of the two sorted arrays.",
        "avg_solve_time": 1800,
        "examples": [
            {"input": "nums1 = [1,3], nums2 = [2]", "output": "2.00000"},
            {"input": "nums1 = [1,2], nums2 = [3,4]", "output": "2.50000"}
        ],
        "test_cases": [
            {"input": "nums1 = [1,3], nums2 = [2]", "expected_output": "2.0", "is_sample": True},
            {"input": "nums1 = [1,2], nums2 = [3,4]", "expected_output": "2.5", "is_sample": True},
            {"input": "nums1 = [0,0], nums2 = [0,0]", "expected_output": "0.0", "is_sample": True},
            {"input": "nums1 = [], nums2 = [1]", "expected_output": "1.0", "is_hidden": True},
            {"input": "nums1 = [2], nums2 = []", "expected_output": "2.0", "is_hidden": True}
        ],
        "template": "class Solution:\n    def findMedianSortedArrays(self, nums1: List[int], nums2: List[int]) -> float:\n        pass"
    },
    {
        "title": "Merge k Sorted Lists",
        "slug": "merge-k-sorted-lists",
        "difficulty": "hard",
        "description": "You are given an array of k linked-lists lists, each linked-list is sorted in ascending order. Merge all the linked-lists into one sorted linked-list and return it.",
        "avg_solve_time": 1800,
        "examples": [
            {"input": "lists = [[1,4,5],[1,3,4],[2,6]]", "output": "[1,1,2,3,4,4,5,6]"},
            {"input": "lists = []", "output": "[]"}
        ],
        "test_cases": [
            {"input": "lists = [[1,4,5],[1,3,4],[2,6]]", "expected_output": "[1,1,2,3,4,4,5,6]", "is_sample": True},
            {"input": "lists = []", "expected_output": "[]", "is_sample": True},
            {"input": "lists = [[]]", "expected_output": "[]", "is_sample": True},
            {"input": "lists = [[1,2,3],[4,5,6]]", "expected_output": "[1,2,3,4,5,6]", "is_hidden": True},
            {"input": "lists = [[1],[0]]", "expected_output": "[0,1]", "is_hidden": True}
        ],
        "template": "class Solution:\n    def mergeKLists(self, lists: List[Optional[ListNode]]) -> Optional[ListNode]:\n        pass"
    },
    {
        "title": "Trapping Rain Water",
        "slug": "trapping-rain-water",
        "difficulty": "hard",
        "description": "Given n non-negative integers representing an elevation map where the width of each bar is 1, compute how much water it can trap after raining.",
        "avg_solve_time": 1500,
        "examples": [
            {"input": "height = [0,1,0,2,1,0,1,3,2,1,2,1]", "output": "6"},
             {"input": "height = [4,2,0,3,2,5]", "output": "9"}
        ],
        "test_cases": [
            {"input": "height = [0,1,0,2,1,0,1,3,2,1,2,1]", "expected_output": "6", "is_sample": True},
            {"input": "height = [4,2,0,3,2,5]", "expected_output": "9", "is_sample": True},
            {"input": "height = [1,2,3,4,3,2,1]", "expected_output": "0", "is_sample": True},
            {"input": "height = [1,0,1]", "expected_output": "1", "is_hidden": True},
            {"input": "height = [2,0,2]", "expected_output": "2", "is_hidden": True}
        ],
        "template": "class Solution:\n    def trap(self, height: List[int]) -> int:\n        pass"
    },
    {
        "title": "Edit Distance",
        "slug": "edit-distance",
        "difficulty": "hard",
        "description": "Given two strings word1 and word2, return the minimum number of operations required to convert word1 to word2. You have the following three operations permitted on a word: Insert, Delete, Replace.",
        "avg_solve_time": 1800,
        "examples": [
            {"input": "word1 = \"horse\", word2 = \"ros\"", "output": "3"},
            {"input": "word1 = \"intention\", word2 = \"execution\"", "output": "5"}
        ],
        "test_cases": [
            {"input": "word1 = \"horse\", word2 = \"ros\"", "expected_output": "3", "is_sample": True},
            {"input": "word1 = \"intention\", word2 = \"execution\"", "expected_output": "5", "is_sample": True},
            {"input": "word1 = \"abc\", word2 = \"abc\"", "expected_output": "0", "is_sample": True},
            {"input": "word1 = \"\", word2 = \"a\"", "expected_output": "1", "is_hidden": True},
            {"input": "word1 = \"teacher\", word2 = \"detather\"", "expected_output": "3", "is_hidden": True}
        ],
        "template": "class Solution:\n    def minDistance(self, word1: str, word2: str) -> int:\n        pass"
    },
    {
        "title": "Largest Rectangle in Histogram",
        "slug": "largest-rectangle-histogram",
        "difficulty": "hard",
        "description": "Given an array of integers heights representing the histogram's bar height where the width of each bar is 1, return the area of the largest rectangle in the histogram.",
        "avg_solve_time": 1800,
        "examples": [
            {"input": "heights = [2,1,5,6,2,3]", "output": "10"},
            {"input": "heights = [2,4]", "output": "4"}
        ],
        "test_cases": [
            {"input": "heights = [2,1,5,6,2,3]", "expected_output": "10", "is_sample": True},
            {"input": "heights = [2,4]", "expected_output": "4", "is_sample": True},
            {"input": "heights = [1,1,1,1]", "expected_output": "4", "is_sample": True},
            {"input": "heights = [0,9]", "expected_output": "9", "is_hidden": True},
            {"input": "heights = [2,1,2]", "expected_output": "3", "is_hidden": True}
        ],
        "template": "class Solution:\n    def largestRectangleArea(self, heights: List[int]) -> int:\n        pass"
    },
    {
        "title": "Sliding Window Maximum",
        "slug": "sliding-window-maximum",
        "difficulty": "hard",
        "description": "You are given an array of integers nums, there is a sliding window of size k which is moving from the very left of the array to the very right. You can only see the k numbers in the window. Return the max sliding window.",
        "avg_solve_time": 1500,
        "examples": [
            {"input": "nums = [1,3,-1,-3,5,3,6,7], k = 3", "output": "[3,3,5,5,6,7]"},
            {"input": "nums = [1], k = 1", "output": "[1]"}
        ],
        "test_cases": [
             {"input": "nums = [1,3,-1,-3,5,3,6,7], k = 3", "expected_output": "[3,3,5,5,6,7]", "is_sample": True},
             {"input": "nums = [1], k = 1", "expected_output": "[1]", "is_sample": True},
             {"input": "nums = [7,2,4], k = 2", "expected_output": "[7,4]", "is_sample": True},
             {"input": "nums = [1,3,1,2,0,5], k = 3", "expected_output": "[3,3,2,5]", "is_hidden": True},
             {"input": "nums = [1,-1], k = 1", "expected_output": "[1,-1]", "is_hidden": True}
        ],
        "template": "class Solution:\n    def maxSlidingWindow(self, nums: List[int], k: int) -> List[int]:\n        pass"
    },
    {
        "title": "Minimum Window Substring",
        "slug": "minimum-window-substring",
        "difficulty": "hard",
        "description": "Given two strings s and t of lengths m and n respectively, return the minimum window substring of s such that every character in t (including duplicates) is included in the window. If there is no such substring, return the empty string \"\".",
        "avg_solve_time": 1800,
        "examples": [
             {"input": "s = \"ADOBECODEBANC\", t = \"ABC\"", "output": "\"BANC\""},
             {"input": "s = \"a\", t = \"a\"", "output": "\"a\""}
        ],
        "test_cases": [
             {"input": "s = \"ADOBECODEBANC\", t = \"ABC\"", "expected_output": "'BANC'", "is_sample": True},
             {"input": "s = \"a\", t = \"a\"", "expected_output": "'a'", "is_sample": True},
             {"input": "s = \"a\", t = \"b\"", "expected_output": "''", "is_sample": True},
             {"input": "s = \"aa\", t = \"aa\"", "expected_output": "'aa'", "is_hidden": True},
             {"input": "s = \"ab\", t = \"a\"", "expected_output": "'a'", "is_hidden": True}
        ],
        "template": "class Solution:\n    def minWindow(self, s: str, t: str) -> str:\n        pass"
    },
    {
        "title": "Reverse Nodes in k-Group",
        "slug": "reverse-nodes-in-k-group",
        "difficulty": "hard",
        "description": "Given the head of a linked list, reverse the nodes of the list k at a time, and return the modified list.",
        "avg_solve_time": 2000,
        "examples": [
            {"input": "head = [1,2,3,4,5], k = 2", "output": "[2,1,4,3,5]"},
            {"input": "head = [1,2,3,4,5], k = 3", "output": "[3,2,1,4,5]"}
        ],
        "test_cases": [
             {"input": "head = [1,2,3,4,5], k = 2", "expected_output": "[2,1,4,3,5]", "is_sample": True},
             {"input": "head = [1,2,3,4,5], k = 3", "expected_output": "[3,2,1,4,5]", "is_sample": True},
             {"input": "head = [1,2,3,4,5], k = 1", "expected_output": "[1,2,3,4,5]", "is_sample": True},
             {"input": "head = [1], k = 1", "expected_output": "[1]", "is_hidden": True},
             {"input": "head = [1,2], k = 2", "expected_output": "[2,1]", "is_hidden": True}
        ],
        "template": "class Solution:\n    def reverseKGroup(self, head: Optional[ListNode], k: int) -> Optional[ListNode]:\n        pass"
    },
    {
        "title": "First Missing Positive",
        "slug": "first-missing-positive",
        "difficulty": "hard",
        "description": "Given an unsorted integer array nums, return the smallest missing positive integer. You must implement an algorithm that runs in O(n) time and uses O(1) auxiliary space.",
        "avg_solve_time": 1500,
        "examples": [
            {"input": "nums = [1,2,0]", "output": "3"},
            {"input": "nums = [3,4,-1,1]", "output": "2"}
        ],
        "test_cases": [
             {"input": "nums = [1,2,0]", "expected_output": "3", "is_sample": True},
             {"input": "nums = [3,4,-1,1]", "expected_output": "2", "is_sample": True},
             {"input": "nums = [7,8,9,11,12]", "expected_output": "1", "is_sample": True},
             {"input": "nums = [1]", "expected_output": "2", "is_hidden": True},
             {"input": "nums = [-1,-2]", "expected_output": "1", "is_hidden": True}
        ],
        "template": "class Solution:\n    def firstMissingPositive(self, nums: List[int]) -> int:\n        pass"
    },
    {
        "title": "N-Queens",
        "slug": "n-queens",
        "difficulty": "hard",
        "description": "The n-queens puzzle is the problem of placing n queens on an n x n chessboard such that no two queens attack each other. Given an integer n, return all distinct solutions to the n-queens puzzle.",
        "avg_solve_time": 2400,
        "examples": [
             {"input": "n = 4", "output": "[[ \".Q..\", \"...Q\", \"Q...\", \"..Q.\" ], [ \"..Q.\", \"Q...\", \"...Q\", \".Q..\" ]]"},
             {"input": "n = 1", "output": "[[\"Q\"]]"}
        ],
        "test_cases": [
             {"input": "n = 4", "expected_output": "[['.Q..', '...Q', 'Q...', '..Q.'], ['..Q.', 'Q...', '...Q', '.Q..']]", "is_sample": True},
             {"input": "n = 1", "expected_output": "[['Q']]", "is_sample": True},
             {"input": "n = 2", "expected_output": "[]", "is_sample": True},
             {"input": "n = 3", "expected_output": "[]", "is_hidden": True},
             {"input": "n = 5", "expected_output": "[['Q....', '..Q..', '....Q', '.Q...', '...Q.'], ['Q....', '...Q.', '.Q...', '....Q', '..Q..'], ['.Q...', '...Q.', 'Q....', '..Q..', '....Q'], ['.Q...', 'Q....', '..Q..', '....Q', '...Q.'], ['..Q..', 'Q....', '...Q.', '.Q...', '....Q'], ['..Q..', '....Q', '.Q...', 'Q....', '...Q.'], ['...Q.', 'Q....', '..Q..', '....Q', '.Q...'], ['...Q.', '.Q...', '....Q', '..Q..', 'Q....'], ['....Q', '.Q...', '...Q.', 'Q....', '..Q..'], ['....Q', '..Q..', 'Q....', '...Q.', '.Q...']]", "is_hidden": True}
        ],
        "template": "class Solution:\n    def solveNQueens(self, n: int) -> List[List[str]]:\n        pass"
    }
]

async def seed_questions():
    async with AsyncSessionLocal() as db:
        logger.info("Cleaning existing data...")
        # Clean existing data to avoid duplicates (optional, based on requirement)
        await db.execute(text("TRUNCATE TABLE questions CASCADE"))
        
        logger.info("Seeding new questions...")
        
        questions_to_add = []
        for q_data in QUESTIONS_DATA:
            question = Question(
                title=q_data["title"],
                slug=q_data["slug"],
                description=q_data["description"],
                difficulty=q_data["difficulty"],
                avg_solve_time=q_data["avg_solve_time"],
                examples=q_data.get("examples")
            )
            
            # Add Test Cases
            question.test_cases = [
                TestCase(
                    input=tc["input"], 
                    expected_output=str(tc["expected_output"]), 
                    is_hidden=tc.get("is_hidden", False),
                    is_sample=tc.get("is_sample", False)
                ) for tc in q_data["test_cases"]
            ]
            
            # Add Templates
            java_params_map = {
                "Two Sum": "int[] nums, int target",
                "Palindrome Number": "int x",
                "Roman to Integer": "String s",
                "Valid Parentheses": "String s",
                "Remove Duplicates from Sorted Array": "int[] nums",
                "Plus One": "int[] digits",
                "Climbing Stairs": "int n",
                "Sqrt(x)": "int x",
                "Length of Last Word": "String s",
                "Search Insert Position": "int[] nums, int target",
                "Letter Combinations of a Phone Number": "String digits",
                "Add Two Numbers": "ListNode l1, ListNode l2",
                "Longest Substring Without Repeating Characters": "String s",
                "Container With Most Water": "int[] height",
                "3Sum": "int[] nums",
                "Generate Parentheses": "int n",
                "Permutations": "int[] nums",
                "Rotate Image": "int[][] matrix",
                "Group Anagrams": "String[] strs",
                "Jump Game": "int[] nums",
                "Median of Two Sorted Arrays": "int[] nums1, int[] nums2",
                "Merge k Sorted Lists": "ListNode[] lists",
                "Trapping Rain Water": "int[] height",
                "Edit Distance": "String word1, String word2",
                "Largest Rectangle in Histogram": "int[] heights",
                "Sliding Window Maximum": "int[] nums, int k",
                "Minimum Window Substring": "String s, String t",
                "Reverse Nodes in k-Group": "ListNode head, int k",
                "First Missing Positive": "int[] nums",
                "N-Queens": "int n"
            }
            java_params = java_params_map.get(q_data["title"], "String s")
            
            cpp_params_map = {
                "Two Sum": "vector<int>& nums, int target",
                "Palindrome Number": "int x",
                "Roman to Integer": "string s",
                "Valid Parentheses": "string s",
                "Remove Duplicates from Sorted Array": "vector<int>& nums",
                "Plus One": "vector<int>& digits",
                "Climbing Stairs": "int n",
                "Sqrt(x)": "int x",
                "Length of Last Word": "string s",
                "Search Insert Position": "vector<int>& nums, int target",
                "Letter Combinations of a Phone Number": "string digits",
                "Add Two Numbers": "ListNode* l1, ListNode* l2",
                "Longest Substring Without Repeating Characters": "string s",
                "Container With Most Water": "vector<int>& height",
                "3Sum": "vector<int>& nums",
                "Generate Parentheses": "int n",
                "Permutations": "vector<int>& nums",
                "Rotate Image": "vector<vector<int>>& matrix",
                "Group Anagrams": "vector<string>& strs",
                "Jump Game": "vector<int>& nums",
                "Median of Two Sorted Arrays": "vector<int>& nums1, vector<int>& nums2",
                "Merge k Sorted Lists": "vector<ListNode*>& lists",
                "Trapping Rain Water": "vector<int>& height",
                "Edit Distance": "string word1, string word2",
                "Largest Rectangle in Histogram": "vector<int>& heights",
                "Sliding Window Maximum": "vector<int>& nums, int k",
                "Minimum Window Substring": "string s, string t",
                "Reverse Nodes in k-Group": "ListNode* head, int k",
                "First Missing Positive": "vector<int>& nums",
                "N-Queens": "int n"
            }
            cpp_params = cpp_params_map.get(q_data["title"], "string s")

            question.templates = [
                CodeTemplate(
                    language="python",
                    template_code=q_data["template"],
                    starter_code=q_data["template"] + "\n        pass"
                ),
                CodeTemplate(
                    language="java",
                    template_code="public class Solution {\n    public " + 
                                  ("int[]" if q_data["title"] == "Two Sum" else 
                                   "boolean" if q_data["title"] == "Palindrome Number" else 
                                   "int" if q_data["title"] == "Roman to Integer" else
                                   "boolean" if q_data["title"] == "Valid Parentheses" else
                                   "int" if q_data["title"] == "Remove Duplicates from Sorted Array" else
                                   "int[]" if q_data["title"] == "Plus One" else
                                   "int" if q_data["title"] == "Climbing Stairs" else
                                   "int" if q_data["title"] == "Sqrt(x)" else
                                   "int" if q_data["title"] == "Length of Last Word" else
                                   "int" if q_data["title"] == "Search Insert Position" else
                                   "List<String>" if q_data["title"] == "Letter Combinations of a Phone Number" else
                                   "ListNode" if q_data["title"] == "Add Two Numbers" else
                                   "int" if q_data["title"] == "Longest Substring Without Repeating Characters" else
                                   "int" if q_data["title"] == "Container With Most Water" else
                                   "List<List<Integer>>" if q_data["title"] == "3Sum" else
                                   "List<String>" if q_data["title"] == "Generate Parentheses" else
                                   "List<List<Integer>>" if q_data["title"] == "Permutations" else
                                   "void" if q_data["title"] == "Rotate Image" else
                                   "List<List<String>>" if q_data["title"] == "Group Anagrams" else
                                   "boolean" if q_data["title"] == "Jump Game" else
                                   "double" if q_data["title"] == "Median of Two Sorted Arrays" else
                                   "ListNode" if q_data["title"] == "Merge k Sorted Lists" else
                                   "int" if q_data["title"] == "Trapping Rain Water" else
                                   "int" if q_data["title"] == "Edit Distance" else
                                   "int" if q_data["title"] == "Largest Rectangle in Histogram" else
                                   "int[]" if q_data["title"] == "Sliding Window Maximum" else
                                   "String" if q_data["title"] == "Minimum Window Substring" else
                                   "ListNode" if q_data["title"] == "Reverse Nodes in k-Group" else
                                   "int" if q_data["title"] == "First Missing Positive" else
                                   "List<List<String>>" if q_data["title"] == "N-Queens" else "void") +
                                  " " + q_data['slug'].replace('-', '') + "(" + java_params + ") {\n        \n    }\n}",
                    starter_code="public class Solution {\n    public " + 
                                  ("int[]" if q_data["title"] == "Two Sum" else 
                                   "boolean" if q_data["title"] == "Palindrome Number" else 
                                   "int" if q_data["title"] == "Roman to Integer" else
                                   "boolean" if q_data["title"] == "Valid Parentheses" else
                                   "int" if q_data["title"] == "Remove Duplicates from Sorted Array" else
                                   "int[]" if q_data["title"] == "Plus One" else
                                   "int" if q_data["title"] == "Climbing Stairs" else
                                   "int" if q_data["title"] == "Sqrt(x)" else
                                   "int" if q_data["title"] == "Length of Last Word" else
                                   "int" if q_data["title"] == "Search Insert Position" else
                                   "List<String>" if q_data["title"] == "Letter Combinations of a Phone Number" else
                                   "ListNode" if q_data["title"] == "Add Two Numbers" else
                                   "int" if q_data["title"] == "Longest Substring Without Repeating Characters" else
                                   "int" if q_data["title"] == "Container With Most Water" else
                                   "List<List<Integer>>" if q_data["title"] == "3Sum" else
                                   "List<String>" if q_data["title"] == "Generate Parentheses" else
                                   "List<List<Integer>>" if q_data["title"] == "Permutations" else
                                   "void" if q_data["title"] == "Rotate Image" else
                                   "List<List<String>>" if q_data["title"] == "Group Anagrams" else
                                   "boolean" if q_data["title"] == "Jump Game" else
                                   "double" if q_data["title"] == "Median of Two Sorted Arrays" else
                                   "ListNode" if q_data["title"] == "Merge k Sorted Lists" else
                                   "int" if q_data["title"] == "Trapping Rain Water" else
                                   "int" if q_data["title"] == "Edit Distance" else
                                   "int" if q_data["title"] == "Largest Rectangle in Histogram" else
                                   "int[]" if q_data["title"] == "Sliding Window Maximum" else
                                   "String" if q_data["title"] == "Minimum Window Substring" else
                                   "ListNode" if q_data["title"] == "Reverse Nodes in k-Group" else
                                   "int" if q_data["title"] == "First Missing Positive" else
                                   "List<List<String>>" if q_data["title"] == "N-Queens" else "void") +
                                  " " + q_data['slug'].replace('-', '') + "(" + java_params + ") {\n        return " + 
                                  ('null' if q_data['title'] == 'Two Sum' or 'ListNode' in q_data['title'] or 'List' in q_data['title'] or '[]' in q_data['title'] else 'false' if q_data['title'] == 'Palindrome Number' or q_data['title'] == 'Valid Parentheses' or q_data['title'] == 'Jump Game' else '0') + ";\n    }\n}"
                ),
                CodeTemplate(
                    language="cpp",
                    template_code="class Solution {\npublic:\n    " + 
                                  ("vector<int>" if q_data["title"] == "Two Sum" else "bool" if q_data["title"] == "Palindrome Number" else "int") +
                                  " " + q_data['slug'].replace('-', ' ').title().replace(' ', '')[0].lower() + q_data['slug'].replace('-', ' ').title().replace(' ', '')[1:] + "(" + cpp_params + ") {\n        \n    }\n};",
                    starter_code="class Solution {\npublic:\n    " + 
                                  ("vector<int>" if q_data["title"] == "Two Sum" else "bool" if q_data["title"] == "Palindrome Number" else "int") +
                                  " " + q_data['slug'].replace('-', ' ').title().replace(' ', '')[0].lower() + q_data['slug'].replace('-', ' ').title().replace(' ', '')[1:] + "(" + cpp_params + ") {\n        return {};\n    }\n};"
                )
            ]
            
            questions_to_add.append(question)
        
        db.add_all(questions_to_add)
        await db.commit()
        logger.info(f"Successfully seeded {len(questions_to_add)} questions!")

if __name__ == "__main__":
    asyncio.run(seed_questions())
