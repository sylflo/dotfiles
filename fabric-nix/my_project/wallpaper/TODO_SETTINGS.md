Usage: swww img [OPTIONS] <PATH>

Arguments:
  <PATH>
          Path to the image to display

Options:
  -o, --outputs <OUTPUTS>
          Comma separated list of outputs to display the image at.
          
          If it isn't set, the image is displayed on all outputs.
          
          [default: ]

      --resize <RESIZE>
          Whether to resize the image and the method by which to resize it
          
          [default: crop]

          Possible values:
          - no:   Do not resize the image
          - crop: Resize the image to fill the whole screen, cropping out parts that don't fit
          - fit:  Resize the image to fit inside the screen, preserving the original aspect ratio

      --fill-color <FILL_COLOR>
          Which color to fill the padding with when output image does not fill screen
          
          [default: 000000]

  -f, --filter <FILTER>
          Filter to use when scaling images (run swww img --help to see options).
          
          Available options are:
          
          Nearest | Bilinear | CatmullRom | Mitchell | Lanczos3
          
          These are offered by the fast_image_resize crate (https://docs.rs/fast_image_resize/2.5.0/fast_image_resize/). 'Nearest' is what I recommend for pixel art stuff, and ONLY for
          pixel art stuff. It is also the fastest filter.
          
          For non pixel art stuff, I would usually recommend one of the last three, though some experimentation will be necessary to see which one you like best. Also note they are all
          slower than Nearest.
          
          [default: Lanczos3]

  -t, --transition-type <TRANSITION_TYPE>
          Sets the type of transition. Default is 'simple', that fades into the new image
          
          Possible transitions are:
          
          none | simple | fade | left | right | top | bottom | wipe | wave | grow | center | any | outer | random
          
          The 'left', 'right', 'top' and 'bottom' options make the transition happen from that position to its opposite in the screen.
          
          'none' is an alias to 'simple' that also sets the 'transition-step' to 255. This has the effect of the transition finishing instantly
          
          'fade' is similar to 'simple' but the fade is controlled through the --transition-bezier flag
          
          'wipe' is similar to 'left' but allows you to specify the angle for transition with the `--transition-angle` flag.
          
          'wave' is similar to 'wipe' sweeping line is wavy
          
          'grow' causes a growing circle to transition across the screen and allows changing the circle's center position with the `--transition-pos` flag.
          
          'center' is an alias to 'grow' with position set to center of screen.
          
          'any' is an alias to 'grow' with position set to a random point on screen.
          
          'outer' is the same as grow but the circle shrinks instead of growing.
          
          Finally, 'random' will select a transition effect at random
          
          [env: SWWW_TRANSITION=]
          [default: simple]

      --transition-step <TRANSITION_STEP>
          How fast the transition approaches the new image.
          
          The transition logic works by adding or subtracting from the current rgb values until the old image transforms in the new one. This controls by how much we add or subtract.
          
          Larger values will make the transition faster, but more abrupt. A value of 255 will always switch to the new image immediately.
          
          This defaults to 2 when transition-type is 'simple', and 90 otherwise
          
          [env: SWWW_TRANSITION_STEP=]
          [default: 90]

      --transition-duration <TRANSITION_DURATION>
          How long the transition takes to complete in seconds.
          
          Note that this doesn't work with the 'simple' transition
          
          [env: SWWW_TRANSITION_DURATION=]
          [default: 3]

      --transition-fps <TRANSITION_FPS>
          Frame rate for the transition effect.
          
          Note there is no point in setting this to a value smaller than what your monitor supports.
          
          Also note this is **different** from the transition-step. That one controls by how much we approach the new image every frame.
          
          [env: SWWW_TRANSITION_FPS=]
          [default: 30]

      --transition-angle <TRANSITION_ANGLE>
          This is used for the 'wipe' and 'wave' transitions. It controls the angle of the wipe
          
          Note that the angle is in degrees, where '0' is right to left and '90' is top to bottom, and '270' bottom to top
          
          [env: SWWW_TRANSITION_ANGLE=]
          [default: 45]

      --transition-pos <TRANSITION_POS>
          This is only used for the 'grow','outer' transitions. It controls the center of circle (default is 'center').
          
          Position values can be given in both percentage values and pixel values: float values are interpreted as percentages and integer values as pixel values eg: 0.5,0.5 means 50% of
          the screen width and 50% of the screen height 200,400 means 200 pixels from the left and 400 pixels from the bottom
          
          the value can also be an alias which will set the position accordingly): 'center' | 'top' | 'left' | 'right' | 'bottom' | 'top-left' | 'top-right' | 'bottom-left' |
          'bottom-right'
          
          [env: SWWW_TRANSITION_POS=]
          [default: center]

      --invert-y
          inverts the y position sent in 'transiiton_pos' flag
          
          [env: INVERT_Y=]

      --transition-bezier <TRANSITION_BEZIER>
          bezier curve to use for the transition https://cubic-bezier.com is a good website to get these values from
          
          eg: 0.0,0.0,1.0,1.0 for linear animation
          
          [env: SWWW_TRANSITION_BEZIER=]
          [default: .54,0,.34,.99]

      --transition-wave <TRANSITION_WAVE>
          currently only used for 'wave' transition to control the width and height of each wave
          
          [env: SWWW_TRANSITION_WAVE=]
          [default: 20,20]

  -h, --help
          Print help (see a summary with '-h')
