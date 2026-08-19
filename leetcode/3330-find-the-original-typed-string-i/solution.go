func possibleStringCount(word string) int {
    ans := 1
    for i := 1; i < len(word); i++ {
        if word[i] == word[i-1] {
            ans++
        }
    }
    return ans
}
