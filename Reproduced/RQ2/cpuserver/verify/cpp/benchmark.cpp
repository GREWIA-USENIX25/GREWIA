#include <chrono>
#include <fstream>
#include <iostream>
#include <regex>
#include <boost/regex.hpp>

void measure(const std::string& data, const std::string& pattern) {
  using clock = std::chrono::high_resolution_clock;
  const auto start = clock::now();

  const REGEX_NAMESPACE::regex re{pattern};
  unsigned count = 0;
  try{
      for (REGEX_NAMESPACE::sregex_token_iterator it{data.cbegin(), data.cend(), re}, end{}; it != end; ++it)
        count++;
  }
  catch (boost::wrapexcept<std::runtime_error> E){
    sleep(1);
  }
  

  const auto end = clock::now();
  const double elapsed = std::chrono::duration_cast<std::chrono::nanoseconds>(end - start).count() * 1e-6;
  std::cout << elapsed << " - " << count << "\n";
}


// void measure(const std::string& data, const std::string& pattern) {
//   using clock = std::chrono::high_resolution_clock;
//   const auto start = clock::now();

//   const REGEX_NAMESPACE::regex re{"^(" + pattern + ")$"};
//   unsigned count = 0;
//   try {
//     if (REGEX_NAMESPACE::regex_match(data, re)) {
//       count = 1;
//     }
//   }
//   catch (boost::wrapexcept<std::runtime_error> E) {
//     sleep(1);
//   }

//   const auto end = clock::now();
//   const double elapsed = std::chrono::duration_cast<std::chrono::nanoseconds>(end - start).count() * 1e-6;
//   std::cout << elapsed << " - " << count << "\n";
// }

int main(int argc, char** argv) {
  if (argc != 3) {
    std::cerr << "Usage: benchmark <filename>\n";
    return 1;
  }

  std::ifstream file{argv[2]};
  if (!file) {
    std::cerr << "unable to open " << argv[2] << "\n";
    return 1;
  }

  const std::string data{std::istreambuf_iterator<char>{file}, std::istreambuf_iterator<char>{}};
  //std::cout << argv[2] << "\n";
  measure(data, argv[1]);
  return 0;
}
