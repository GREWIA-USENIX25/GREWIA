var filename;
var regex;

process.argv.forEach(function (val, index, array) {
    if (index == 2){
        regex = val;
    }
    if (index == 3){
        filename = val;
    }
  });
const fs = require('fs');

fs.readFile(filename, 'utf8', (err, data) => {
    if (err) {
      console.error(err);
      return;
    }
    // var myRe = new RegExp(regex, "g");
    // var result = myRe.exec(data)

    var result = data.search(new RegExp(regex, "g"));
});

// fs.readFile(filename, 'utf8', (err, data) => {
//   if (err) {
//     console.error(err);
//     return;
//   }
//   // console.log(regex);
//   var regex_ = new RegExp("^(" + regex + ")$");
//   // console.log(regex_);
//   var result = regex_.test(data);
//   console.log(result);
// });