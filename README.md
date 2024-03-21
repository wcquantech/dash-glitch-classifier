# GW Glitch Classifier

Welcome to the GW Glitch Classifier repository! This application is designed to classify gravitational wave signals into various glitch classes using pre-trained deep learning models. It's a simple yet powerful tool for researchers and enthusiasts in the field of gravitational wave astronomy.

## Features

- **Upload and Classify**: Users can upload gravitational wave signals in HDF5 format and classify them into one of the 23 glitch classes.
- **Deep Learning Models**: Utilizes pre-trained models based on Inception-V3 and GoogleNet architectures for accurate classification.
- **Visualization**: Provides visualizations of the gravitational wave signal and its classification results.


## Usage

Once the application is running, navigate to the web interface where you can upload your HDF5 file and select the model for classification. The application will display the classification results along with the confidence scores.

## Use Locally

To use the GW Glitch Classifier locally, follow these steps:
1. Clone the repository to your local machine.
2. Ensure you have Python installed and set up a virtual environment.
3. Install the required Python packages using `pip install -r requirements.txt`.
4. Create a `.env` file in the root directory and set the `UPLOAD_PATH` variable (e.g., `UPLOAD_PATH=files`).
5. Start the application by running `python src/app.py`.


## Contributing

Contributions to the GW Glitch Classifier are welcome! Whether it's bug reports, feature requests, or code contributions, please feel free to make a contribution.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- This project utilizes models trained by Jianqi Yan and Alex P Leung.
- Special thanks to the Gravity Spy project and the Zooniverse platform for their contributions to the field.

Thank you for visiting the GW Glitch Classifier repository!