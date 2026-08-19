func longestCommonPrefix(strs []string) string {
	// Edge case: if the slice is empty, return an empty string immediately
	if len(strs) == 0 {
		return ""
	}

	// Use the first string as a reference point for character comparison
	firstStr := strs[0]

	// Iterate through each character of the first string
	for i := 0; i < len(firstStr); i++ {
		char := firstStr[i]

		// Compare this character with the same index across all other strings
		for j := 1; j < len(strs); j++ {
			// Stop if the current string is shorter than the index 'i'
			// OR if a character mismatch is detected
			if i >= len(strs[j]) || strs[j][i] != char {
				return firstStr[:i] // Return substring up to index 'i' (exclusive)
			}
		}
	}

	// If no mismatch occurs, the entire first string is the common prefix
	return firstStr
}