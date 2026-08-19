func isPalindrome(x int) bool {
    // Negative numbers and numbers ending in 0 (except 0 itself) cannot be palindromes
    if x < 0 || (x % 10 == 0 && x != 0) {
        return false
    }

    revertedNumber := 0
    // Reverse the second half of the number
    for x > revertedNumber {
        revertedNumber = revertedNumber * 10 + x % 10
        x /= 10
    }

    // For even length: x == revertedNumber
    // For odd length: x == revertedNumber / 10 (gets rid of the middle digit)
    return x == revertedNumber || x == revertedNumber / 10
}
