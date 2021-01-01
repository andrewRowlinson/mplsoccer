""" mplsoccer pitch dimensions.

Note that for tracab, uefa, metricasports, custom, and skillcorner the dimensions are in meters
(or centimeters for tracab). Real-life pictures are in actually measured in yards and the meter conversions
are slightly different, but for the purposes of the visualisations the differences will be minimal.

Wycout dimensions are sourced from ggsoccer https://github.com/Torvaney/ggsoccer/blob/master/R/dimensions.R
Note, the goal width in ggsoccer (12 units) is different from socceraction (10 units)
(https://github.com/ML-KULeuven/socceraction/blob/master/socceraction/spadl/wyscout.py),
I am not sure which is correct, but I have gone for the goal width from ggsoccer (12 units).
In the previous versions of mplsoccer (up to 0.0.21), I used the socceraction goal width (10 units)."""

valid = ['statsbomb', 'tracab', 'opta', 'wyscout', 'uefa',
         'metricasports', 'custom', 'skillcorner', 'secondspectrum']
size_varies = ['tracab', 'metricasports', 'custom', 'skillcorner', 'secondspectrum']

statsbomb = {'top': 0, 'bottom': 80, 'left': 0, 'right': 120, 'aspect': 1,
             'width': 80, 'center_width': 40, 'length': 120, 'center_length': 60,
             'six_yard_from_side': 30, 'six_yard_width': 20, 'six_yard_length': 6,
             'penalty_area_from_side': 18, 'penalty_area_width': 44, 'penalty_area_length': 18,
             'left_penalty': 12, 'right_penalty': 108, 'circle_diameter': 20.,
             'goal_depth': 2.4, 'goal_width': 8, 'goal_post': 36,
             'arc': 53.05, 'invert_y': True, 'origin_center': False}

tracab = {'center_width': 0, 'center_length': 0, 'aspect': 1,
          'six_yard_from_side': -916, 'six_yard_width': 1832, 'six_yard_length': 550,
          'penalty_area_from_side': -2016, 'penalty_area_width': 4032, 'penalty_area_length': 1650,
          'circle_diameter': 1830, 'goal_depth': 200, 'goal_width': 732, 'goal_post': -366,
          'arc': 53.05, 'invert_y': False, 'origin_center': True}

opta = {'top': 100, 'bottom': 0, 'left': 0, 'right': 100, 'aspect': 68/105,
        'width': 100, 'center_width': 50, 'length': 100, 'center_length': 50,
        'six_yard_from_side': 36.8, 'six_yard_width': 26.4, 'six_yard_length': 5.8,
        'penalty_area_from_side': 21.1, 'penalty_area_width': 57.8, 'penalty_area_length': 17.0,
        'left_penalty': 11.5, 'right_penalty': 88.5, 'circle_diameter': 17.68,
        'goal_depth': 1.9, 'goal_width': 10.76, 'goal_post': 44.62, 'invert_y': False, 'origin_center': False}

# wyscout dimensions are sourced 
wyscout = {'top': 0, 'bottom': 100, 'left': 0, 'right': 100, 'aspect': 68/105,
           'width': 100, 'center_width': 50, 'length': 100, 'center_length': 50,
           'six_yard_from_side': 37, 'six_yard_width': 26, 'six_yard_length': 6,
           'penalty_area_from_side': 19, 'penalty_area_width': 62, 'penalty_area_length': 16,
           'left_penalty': 10, 'right_penalty': 90, 'circle_diameter': 17.68,
           'goal_depth': 1.9, 'goal_width': 12, 'goal_post': 45, 'invert_y': True, 'origin_center': False}

uefa = {'top': 68, 'bottom': 0, 'left': 0, 'right': 105, 'aspect': 1,
        'width': 68, 'center_width': 34, 'length': 105, 'center_length': 52.5,
        'six_yard_from_side': 24.84, 'six_yard_width': 18.32, 'six_yard_length': 5.5,
        'penalty_area_from_side': 13.84, 'penalty_area_width': 40.32,
        'penalty_area_length': 16.5, 'left_penalty': 11, 'right_penalty': 94,
        'circle_diameter': 18.3, 'goal_depth': 2, 'goal_width': 7.32, 'goal_post': 30.34,
        'arc': 53.05, 'invert_y': False, 'origin_center': False}

metricasports = {'top': 0., 'bottom': 1., 'left': 0., 'right': 1.,
                 'width': 1, 'center_width': 0.5, 'length': 1, 'center_length': 0.5,
                 'six_yard_width': 18.32, 'six_yard_length': 5.5,
                 'penalty_area_width': 40.32,
                 'penalty_area_length': 16.5, 'left_penalty': 11., 'right_penalty': 11., 'circle_diameter': 18.3,
                 'goal_depth': 2., 'goal_width': 7.32, 'goal_post': 3.6,
                 'invert_y': True, 'origin_center': False}

custom = {'bottom': 0., 'left': 0., 'aspect': 1, 'six_yard_width': 18.32, 'six_yard_length': 5.5,
          'penalty_area_width': 40.32, 'left_penalty': 11., 'penalty_area_length': 16.5,  'circle_diameter': 18.3,
          'goal_depth': 2., 'goal_width': 7.32, 'arc': 53.05, 'invert_y': False, 'origin_center': False}

skillcorner_secondspectrum = {'center_width': 0, 'center_length': 0, 'aspect': 1,
                              'six_yard_from_side': -9.16, 'six_yard_width': 18.32,
                              'six_yard_length': 5.5, 'penalty_area_from_side': -20.16,
                              'penalty_area_width': 40.32, 'penalty_area_length': 16.5,
                              'circle_diameter': 18.3, 'goal_depth': 2, 'goal_width': 7.32,
                              'goal_post': -3.66, 'arc': 53.05, 'invert_y': False,
                              'origin_center': True}
