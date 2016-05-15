
  #include "tinytune/tinytune.h"
  // Envelopes
  
  static int16_t slopes_0[] = {-174, 3264, -68};
  static uint8_t pticks_0[] = {188, 4, 192};
  static struct TTENVELOPE env_0 = {
    .num_points = 3,
    .starting_level = 255,
    .env_slopes = slopes_0,
    .point_ticks = pticks_0,
    .sustain_tick = 16
  };
  

  static int16_t slopes_1[] = {0, -430, 116, -68};
  static uint8_t pticks_1[] = {4, 76, 112, 192};
  static struct TTENVELOPE env_1 = {
    .num_points = 4,
    .starting_level = 255,
    .env_slopes = slopes_1,
    .point_ticks = pticks_1,
    .sustain_tick = 0
  };
  

  static int16_t slopes_2[] = {0, -816, 3440, -594, -5};
  static uint8_t pticks_2[] = {8, 40, 8, 44, 255};
  static struct TTENVELOPE env_2 = {
    .num_points = 5,
    .starting_level = 255,
    .env_slopes = slopes_2,
    .point_ticks = pticks_2,
    .sustain_tick = 255
  };
  
  // Patterns
  static const uint8_t pattern_0[] PROGMEM = {
5, 1, 0, 173, 224, 21, 0, 24, 73, 19, 37, 0, 40, 73, 19, 16, 76, 19, 32, 76,
19, 16, 78, 19, 32, 78, 19, 16, 83, 19, 32, 83, 83, 16, 76, 19, 32, 76, 19, 16,
78, 19, 32, 78, 67, 17, 3, 0, 44, 19, 33, 19, 16, 71, 19, 32, 71, 19, 16, 75,
19, 32, 75, 19, 16, 76, 19, 32, 76, 83, 16, 78, 19, 32, 78, 19, 16, 75, 19, 32,
75, 19, 16, 71, 51
};
static const uint8_t pattern_1[] PROGMEM = {
5, 1, 8, 37, 21, 0, 24, 75, 19, 37, 0, 40, 75, 147, 16, 73, 19, 32, 73, 147,
16, 68, 19, 32, 68, 83, 0, 35, 67, 17, 35, 33, 115, 16, 73, 19, 32, 73, 19, 16,
78, 19, 32, 78, 19, 16, 80, 19, 32, 80, 19, 16, 85, 19, 32, 85, 19
};
static const uint8_t pattern_2[] PROGMEM = {
5, 2, 8, 45, 22, 197, 8, 23, 21, 0, 24, 87, 37, 0, 40, 61, 51, 32, 63, 51,
0, 45, 17, 32, 64, 51, 16, 85, 32, 66, 51, 0, 45, 32, 68, 35, 17, 3, 32, 71,
51, 0, 45, 16, 92, 32, 73, 51, 32, 76, 51, 0, 44, 16, 90, 32, 83, 51, 32, 80,
51, 0, 44, 23, 16, 95, 32, 76, 51, 16, 87, 32, 73, 51, 0, 44, 32, 78, 51, 32,
75, 51, 0, 44, 16, 83, 32, 71, 51, 32, 68, 51
};
static const uint8_t pattern_3[] PROGMEM = {
5, 1, 0, 165, 224, 21, 0, 24, 75, 33, 36, 255, 115, 8, 42, 16, 76, 115, 0, 44,
16, 75, 83, 0, 47, 16, 71, 99, 0, 44, 16, 75, 99, 0, 49, 16, 73, 51, 1, 17,
115, 0, 189, 224, 19, 8, 56, 19, 0, 54, 19, 0, 49, 19, 0, 54, 19, 0, 49, 19,
0, 44, 19, 0, 37, 19
};

  static const uint8_t* const p_dat[] PROGMEM = {pattern_0,
pattern_1,
pattern_2,
pattern_3};
  static const uint16_t p_len[] PROGMEM = {85, 57, 92, 66};
  static const uint8_t p_ord[] PROGMEM = {0, 1, 2, 3};
  static const struct TTENVELOPE* envs[] = {&env_0, &env_1, &env_2};
  struct song_definition luna = {
  .pattern_data = p_dat,
  .num_patterns = 4,
  .pattern_lengths = p_len,
  .pattern_order = p_ord,
  .bpm = 160,
  .rows_per_beat = 8,
  .ticks_per_row = 12,
  .envelopes = envs,
  };
    