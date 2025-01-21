// Function to generate an array of random numbers
export function getRandomNumbers(count, min = 1, max = 5) {
    const randomNumbers = [];
    for (let i = 0; i < count; i++) {
        const randomNumber = Math.random() * (max - min) + min;
        randomNumbers.push(Number(randomNumber.toFixed(2))); // Round to 2 decimal places
    }
    return randomNumbers;
}