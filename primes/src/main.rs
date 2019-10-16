extern crate clap;

use clap::{Arg, App};

fn is_factor(n: i32, f: i32) -> bool {
    n % f == 0
}

fn factorize(n: i32) -> Vec<i32> {
    let mut factors = vec![];
    let mut i: i32 = 0;

    while i < n {
        i += 1;
        if is_factor(n, i) {
            factors.push(i);
        }
    }

    factors
}

fn is_prime(n: i32) -> bool {
    let factors: Vec<i32> = factorize(n);
    factors.len() == 2
}

fn primes_to_limit(limit: i32) -> Vec<i32> {
    let mut primes = vec![];
    let mut i: i32 = 1;

    while i < limit {
        i += 1;
        if is_prime(i) {
            println!("{}", i);
            primes.push(i);
        }
    }

    primes
}

fn main() {
    let matches = App::new("Primes")
        .version("0.1.0")
        .author("Jack Reid <emailjackreid@gmail.com")
        .about("Generates prime numbers")
        .arg(Arg::with_name("limit")
            .short("l")
            .value_name("LIMIT")
            .help("The number to generate prime numbers up to")
            .required(true)
        )
        .get_matches();

    let limit = matches.value_of("limit").unwrap().parse::<i32>().unwrap();
    let primes: Vec<i32> = primes_to_limit(limit);

    println!("\n{} primes below {}", limit, primes.len());
}

#[cfg(test)]
mod tests {
    use super::is_factor;
    use super::factorize;
    use super::is_prime;
    use super::primes_to_limit;

    #[test]
    fn test_is_factor() {
        assert_eq!(true, is_factor(3, 1));
        assert_eq!(true, is_factor(9, 3));
        assert_eq!(true, is_factor(27, 9));
        assert_eq!(true, is_factor(27, 3));
        assert_eq!(false, is_factor(9, 2));
        assert_eq!(false, is_factor(10, 3));
        assert_eq!(false, is_factor(2, 4));
        assert_eq!(false, is_factor(40, 11));
    }

    #[test]
    fn test_factorize() {
        assert_eq!(vec![1], factorize(1));
        assert_eq!(vec![1, 3], factorize(3));
        assert_eq!(vec![1, 2, 4, 5, 10, 20, 25, 50, 100], factorize(100));
    }

    #[test]
    fn test_is_prime() {
        assert_eq!(true, is_prime(2));
        assert_eq!(true, is_prime(7));
        assert_eq!(true, is_prime(13));
        assert_eq!(true, is_prime(117529));
        assert_eq!(false, is_prime(1));
        assert_eq!(false, is_prime(10));
        assert_eq!(false, is_prime(33));
        assert_eq!(false, is_prime(10000002));
    }

    #[test]
    fn test_primes_to_limit() {
        assert_eq!(vec![2], primes_to_limit(2));
        assert_eq!(vec![2, 3, 5], primes_to_limit(5));
        assert_eq!(vec![2, 3, 5, 7], primes_to_limit(10));
    }
}