// ask for a file to be imported
fileName = File.openDialog("Select the file to import");
allText = File.openAsString(fileName);
tmp = split(fileName,".");
// get file format {txt, csv}
posix = tmp[lengthOf(tmp)-1];
// parse text by lines
text = split(allText, "\n");
 
// define array for points
var xpoints = newArray;
var ypoints = newArray; 

// in case input is in CSV format

print("importing CSV point set...");
//these are the column indexes
hdr = split(text[0]);
iLabel = 0; iX = 3; iY = 4;
// loading and parsing each line
for (i = 1; i < (text.length); i++){
   line = split(text[i],",");
   setOption("ExpandableArrays", true);   
   xpoints[(i-1)%5] = parseInt(line[iX]);
   ypoints[(i-1)%5] = parseInt(line[iY]);
   print("p("+i+") ["+xpoints[(i-1)%5]+"; "+ypoints[(i-1)%5]+"]");
   if (i % 5 == 0) {
   	  setSlice(i / 5);
	  makeSelection("point", xpoints, ypoints);
      xpoints = newArray;
      ypoints = newArray; 
   }
} 

 
