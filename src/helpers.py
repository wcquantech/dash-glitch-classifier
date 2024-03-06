from gwpy.timeseries import TimeSeries
import torchvision.transforms as transforms
import io
import base64
from PIL import Image

# Find the GPS time of the data
def find_gps(hdf5):
    data = TimeSeries.read(hdf5, format="hdf5.gwosc")
    return data.t0.value

# Plotting the strain data in duration 4s
def plot_4s_strain(hdf5, start, end):
    data = TimeSeries.read(hdf5, format="hdf5.gwosc")
    gps = data.t0.value

    # Plot the data in time domain
    tdata = TimeSeries.read(hdf5, format="hdf5.gwosc", start=gps+start, end=gps+end)
    plot = tdata.plot(figsize=[8, 4])
    ax = plot.gca()
    ax.set_epoch(gps)
    ax.set_title("Time-domain")
    ax.set_ylabel("Strain Amplitude []")
    buf1 = io.BytesIO()
    plot.save(buf1, format="png")
    plot.close()

    # Perform Q Transform and plot the result
    target = (2 * gps + start + end) / 2
    tq = tdata.q_transform(frange=(10, 1000), outseg=(target-2, target+2))
    plot = tq.plot(figsize=[8, 4])
    ax = plot.gca()
    ax.set_title("Q-Transformed")
    ax.set_yscale("log")
    ax.set_ylim(10, 1000)
    ax.set_epoch(gps)
    buf2 = io.BytesIO()
    plot.save(buf2, format="png")
    plot.close()

    # Combine the graph
    img1 = Image.open(buf1)
    img2 = Image.open(buf2)
    concat = Image.new("RGB", (img1.width, img1.height + img2.height))
    concat.paste(img1, (0, 0))
    concat.paste(img2, (0, img1.height))

    buf = io.BytesIO()
    concat.save(buf, format="PNG")
    buf.seek(0)
    encoded = base64.b64encode(buf.read()).decode("ascii").replace("\n", "")

    return f"data:image/png;base64,{encoded}"


# Perform Multi-duration Q Transform and return the plotting
def plot_final_spectrogram(hdf5, start, end, save=False, to_predict=False):

    tranges = [0.5, 1, 2]
    transform = transforms.Grayscale()

    data = TimeSeries.read(hdf5, format="hdf5.gwosc")
    gps = data.t0.value
    tdata = TimeSeries.read(hdf5, format="hdf5.gwosc", start=gps+start, end=gps+end)

    target = (2*gps+start+end)/2

    # 1s duration image as R 
    tq1 = tdata.q_transform(frange=(10, 1000), outseg=(target-tranges[0], target+tranges[0]))
    plot1 = tq1.plot(figsize=[5, 5])
    ax1 = plot1.gca()
    ax1.set_epoch(gps)
    ax1.set_ylim(10, 1000)
    ax1.set_yscale("log")
    ax1.grid(False, axis="y", which="both")
    ax1.axis("off")
    buf = io.BytesIO()
    plot1.save(buf, format="png", bbox_inches="tight", pad_inches=0)
    plot1.close()
    r = transform(Image.open(buf))

    # 2s duration image as G
    tq2 = tdata.q_transform(frange=(10, 1000), outseg=(target-tranges[1], target+tranges[1]))
    plot2 = tq2.plot(figsize=[5, 5])
    ax2 = plot2.gca()
    ax2.set_epoch(gps)
    ax2.set_ylim(10, 1000)
    ax2.set_yscale("log")
    ax2.grid(False, axis="y", which="both")
    ax2.axis("off")
    buf = io.BytesIO()
    plot2.save(buf, format="png", bbox_inches="tight", pad_inches=0)
    plot2.close()
    g = transform(Image.open(buf))

    # 4s duration image as B
    tq4 = tdata.q_transform(frange=(10, 1000), outseg=(target-tranges[2], target+tranges[2]))
    plot4 = tq4.plot(figsize=[5, 5])
    ax4 = plot4.gca()
    ax4.set_epoch(gps)
    ax4.set_ylim(10, 1000)
    ax4.set_yscale("log")
    ax4.grid(False, axis="y", which="both")
    ax4.axis("off")
    buf = io.BytesIO()
    plot4.save(buf, format="png", bbox_inches="tight", pad_inches=0)
    plot4.close()
    b = transform(Image.open(buf))

    # Combine the plots
    combination = Image.merge("RGB", (r, g, b))

    if save:
        figname = str(int(target)) + "_transformed.png"
        combination.save(figname)

    buf = io.BytesIO()
    combination.save(buf, format="PNG")

    if to_predict:
        return buf

    else:            
        buf.seek(0)
        encoded = base64.b64encode(buf.read()).decode("ascii").replace("\n", "")
        return f"data:image/png;base64,{encoded}"

