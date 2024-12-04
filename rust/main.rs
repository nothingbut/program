fn main() {
    let arr = [1, 2, 3, 4, 5];
    let slice: &[i32] = &arr;

    // Get a subset of elements using range notation
    let subset_slice = &slice[1..3];

    // Get the length (number of elements) in the slice
    let len = slice.len();

    // Iterate over each element in the slice
    for elem in slice.iter() {
        println!("{}", elem);
    }

    // Find the index of an element
    let idx = slice.iter().position(|&x| x == 4).unwrap();
    println!("{}", idx);
}