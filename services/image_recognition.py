import numpy as np
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras import layers, models
from tensorflow.keras.preprocessing import image


def prepare_model():
    pass
    # model = models.Sequential([
    #     layers.Conv2D(32, (3, 3), activation='relu', input_shape=(224, 224, 3)),
    #     layers.MaxPooling2D((2, 2)),
    #     layers.Conv2D(64, (3, 3), activation='relu'),
    #     layers.MaxPooling2D((2, 2)),
    #     layers.Conv2D(128, (3, 3), activation='relu'),
    #     layers.MaxPooling2D((2, 2)),
    #     layers.Flatten(),
    #     layers.Dense(64, activation='relu'),
    #     layers.Dense(2, activation='softmax')
    # ])
    # model.load_weights('services/my_model.weights.h5')
    # model.compile(optimizer='adam',
    #               loss='sparse_categorical_crossentropy',
    #               metrics=['accuracy'])
    # return model


def predict_image(input_image, model):
    pass
    # Preprocess the input image
    # img = image.load_img(input_image, target_size=(224, 224))
    # img_array = image.img_to_array(img)
    # img_array = np.expand_dims(img_array, axis=0)
    # img_array /= 255.
    #
    # predictions = model.predict(img_array)
    #
    # predicted_labels = np.argmax(predictions, axis=1)
    # label_encoder = LabelEncoder()
    # label_encoder.fit_transform(["honey", "charger"])
    # predicted_class_label = label_encoder.inverse_transform(predicted_labels)
    #
    # predicted_class_index = np.argmax(predictions)
    # print("Prediction:", predictions)
    # print("Prediction argmax:", np.argmax(predictions))
    #
    # print("Predicted class:", predicted_class_label)
    #
    # return predicted_class_label
