import os.path

# 1 get files
from test_completeness import generate_test_completeness_plot_from_csv

for dirpath, dirnames, filenames in os.walk("..\Lang"):
    for filename in [f for f in filenames if f.endswith("killMap.csv")]:
        print(os.path.join(dirpath, filename))

        plot = generate_test_completeness_plot_from_csv(
            os.path.join(dirpath, filename))[1]

        # save the plot

        image_name = dirpath.replace("\\", "-")
        # TODO fix size
        plot.savefig("images\\" + image_name + ".png", dpi=500)
