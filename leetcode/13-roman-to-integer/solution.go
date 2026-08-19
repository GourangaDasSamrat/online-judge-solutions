func romanToInt(s string) int {
    var total, maxVal int
    
    // Traverse from right to left
    for i := len(s) - 1; i >= 0; i-- {
        var currentVal int
        
        // Quick lookups using a switch instead of a map allocation
        switch s[i] {
        case 'I': currentVal = 1
        case 'V': currentVal = 5
        case 'X': currentVal = 10
        case 'L': currentVal = 50
        case 'C': currentVal = 100
        case 'D': currentVal = 500
        case 'M': currentVal = 1000
        }
        
        // Subtraction rule: if current value is less than the max seen to its right
        if currentVal < maxVal {
            total -= currentVal
        } else {
            total += currentVal
            maxVal = currentVal
        }
    }
    
    return total
}
