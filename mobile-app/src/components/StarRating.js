import React from "react";
import { View, Text, TouchableOpacity, StyleSheet } from "react-native";
import { Colors } from "../theme/colors";

export default function StarRating({ rating = 0, onRate, maxStars = 5, size = 28 }) {
  return (
    <View style={styles.container}>
      {[...Array(maxStars)].map((_, i) => {
        const starNum = i + 1;
        const isFilled = starNum <= rating;
        return (
          <TouchableOpacity
            key={i}
            activeOpacity={0.7}
            onPress={() => onRate && onRate(starNum)}
            style={styles.starTouch}
          >
            <Text style={[styles.starText, { fontSize: size, color: isFilled ? Colors.star : "#CBD5E1" }]}>
              ★
            </Text>
          </TouchableOpacity>
        );
      })}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: "row",
    alignItems: "center",
    marginVertical: 6
  },
  starTouch: {
    paddingHorizontal: 4
  },
  starText: {
    fontWeight: "bold"
  }
});
