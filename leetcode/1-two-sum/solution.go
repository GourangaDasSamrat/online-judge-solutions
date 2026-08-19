func twoSum(nums []int, target int) []int {
    // Create a map to store the value as the key and its index as the value
    seen := make(map[int]int)
    
    for i, num := range nums {
        // Calculate the complement needed to reach the target
        complement := target - num
        
        // Check if the complement already exists in our map
        if index, found := seen[complement]; found {
            // If found, return the index of the complement and the current index
            return []int{index, i}
        }
        
        // If not found, store the current number and its index in the map
        seen[num] = i
    }
    
    // Return nil if no solution is found 
    return nil
}