import PiCamUtil

empty = PiCamUtil.pngToGrayArray("Images/empty.png")
half_full = PiCamUtil.pngToGrayArray("Images/half_full.png")

test = PiCamUtil.Collection(2)
test.SetMaxAllowedDiffForEmpty(5000)
numEmpty = test.CompareImgs(empty, half_full)
print("Available spots ",numEmpty) 
