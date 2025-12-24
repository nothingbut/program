# PlayerControls Component Manual Testing Guide

This document provides manual testing instructions for the PlayerControls component to verify all functionality works correctly in the browser.

## Test Setup

1. Start the development server: `bun run dev`
2. Open the application in a browser
3. Add a music directory with MP3 files
4. Select a directory to load tracks into the playlist

## Test Cases

### 1. Track Information Display

**Test**: Verify track information is displayed correctly

**Steps**:
1. Select a track from the playlist (double-click to play)
2. Observe the player controls at the bottom

**Expected Results**:
- [ ] Current track title, artist, and album are displayed
- [ ] Track information follows format: "Album(TrackNumber): Title - Artist"
- [ ] If track has cover art, it should be displayed as a 48x48 thumbnail
- [ ] If no cover art, a music note icon (♪) should be displayed
- [ ] File name should be shown below the track info
- [ ] When no track is selected, "No track selected" message is shown

### 2. Play/Pause Button

**Test**: Verify play/pause functionality

**Steps**:
1. Select a track from the playlist
2. Click the play/pause button (large circular button in center)
3. Click it again to pause
4. Try keyboard shortcut (Spacebar)

**Expected Results**:
- [ ] Button shows play icon (▶) when paused
- [ ] Button shows pause icon (⏸) when playing
- [ ] Button is disabled when no track is selected
- [ ] Spacebar toggles play/pause when not focused on input elements
- [ ] Button has hover effects and proper styling

### 3. Previous/Next Buttons

**Test**: Verify track navigation

**Steps**:
1. Play a track from the middle of the playlist
2. Click the previous button (⏮)
3. Click the next button (⏭)
4. Try keyboard shortcuts (Left/Right arrows)

**Expected Results**:
- [ ] Previous button navigates to previous track in playlist
- [ ] Next button navigates to next track in playlist
- [ ] Buttons are disabled when no track is selected
- [ ] Left arrow key triggers previous track
- [ ] Right arrow key triggers next track
- [ ] Buttons have proper hover effects

### 4. Shuffle Mode Toggle

**Test**: Verify shuffle mode functionality

**Steps**:
1. Click the shuffle button (🔀) to enable shuffle mode
2. Click it again to disable shuffle mode
3. Observe visual feedback

**Expected Results**:
- [ ] Button shows active state (highlighted) when shuffle is enabled
- [ ] Button shows inactive state when shuffle is disabled
- [ ] Button has proper hover effects
- [ ] Visual feedback clearly indicates current state

### 5. Progress Bar

**Test**: Verify progress bar functionality

**Steps**:
1. Play a track
2. Observe the progress bar as the track plays
3. Click on different positions on the progress bar
4. Drag the progress handle to different positions

**Expected Results**:
- [ ] Progress bar fills as the track plays
- [ ] Progress handle appears on hover
- [ ] Clicking on progress bar seeks to that position
- [ ] Dragging the handle seeks to the dragged position
- [ ] Progress bar is responsive and smooth
- [ ] Handle becomes visible and larger when dragging

### 6. Time Display

**Test**: Verify time information

**Steps**:
1. Play a track
2. Observe the time displays on either side of the progress bar
3. Seek to different positions and verify time updates

**Expected Results**:
- [ ] Current time is displayed on the left (format: M:SS)
- [ ] Total duration is displayed on the right (format: M:SS)
- [ ] Times update in real-time during playback
- [ ] Times update immediately when seeking
- [ ] Times are properly formatted with leading zeros for seconds

### 7. Volume Control

**Test**: Verify volume functionality

**Steps**:
1. Locate the volume slider on the right side
2. Drag the volume slider to different positions
3. Observe the volume icon changes

**Expected Results**:
- [ ] Volume slider adjusts playback volume
- [ ] Volume icon changes based on volume level:
  - Muted icon when volume is 0
  - Low volume icon when volume < 0.5
  - High volume icon when volume >= 0.5
- [ ] Slider is responsive and smooth
- [ ] Volume changes are applied immediately

### 8. Keyboard Shortcuts

**Test**: Verify keyboard shortcuts work correctly

**Steps**:
1. Ensure focus is not on any input elements
2. Press Spacebar
3. Press Left Arrow
4. Press Right Arrow
5. Try shortcuts while focused on volume slider

**Expected Results**:
- [ ] Spacebar toggles play/pause
- [ ] Left arrow triggers previous track
- [ ] Right arrow triggers next track
- [ ] Shortcuts are ignored when focused on input elements (volume slider)
- [ ] Shortcuts work from anywhere in the application

### 9. Responsive Design

**Test**: Verify component adapts to different screen sizes

**Steps**:
1. Resize the browser window to different widths
2. Test on mobile viewport sizes
3. Observe layout changes

**Expected Results**:
- [ ] On desktop (>1024px): All elements in single row
- [ ] On tablet (768-1024px): Track info and volume control are smaller
- [ ] On mobile (<768px): Elements stack vertically
- [ ] On small mobile (<480px): Buttons are smaller, minimal spacing
- [ ] All elements remain accessible and usable at all sizes

### 10. Error Handling

**Test**: Verify component handles edge cases gracefully

**Steps**:
1. Test with tracks that have missing metadata
2. Test with tracks that have very long titles/artist names
3. Test with tracks that have no cover art
4. Test seeking beyond track duration

**Expected Results**:
- [ ] Missing metadata shows "Unknown" or appropriate defaults
- [ ] Long text is truncated with ellipsis
- [ ] Missing cover art shows placeholder icon
- [ ] Seeking is clamped to valid range (0 to duration)
- [ ] No JavaScript errors in console
- [ ] Component remains functional in all scenarios

### 11. Visual Polish

**Test**: Verify visual design and animations

**Steps**:
1. Interact with all buttons and controls
2. Observe hover states and transitions
3. Check dark mode compatibility (if system supports it)

**Expected Results**:
- [ ] All buttons have smooth hover transitions
- [ ] Progress bar handle appears smoothly on hover
- [ ] Colors and contrast are appropriate
- [ ] Dark mode styling works correctly (if applicable)
- [ ] Icons are crisp and properly sized
- [ ] Overall design is consistent with other components

## Performance Testing

### 12. Performance

**Test**: Verify component performs well

**Steps**:
1. Play tracks and observe CPU usage
2. Rapidly seek through tracks
3. Quickly toggle between tracks

**Expected Results**:
- [ ] Smooth animations without stuttering
- [ ] Responsive to user interactions
- [ ] No memory leaks during extended use
- [ ] Progress updates don't cause performance issues

## Accessibility Testing

### 13. Accessibility

**Test**: Verify component is accessible

**Steps**:
1. Navigate using only keyboard (Tab, Enter, Space, Arrows)
2. Test with screen reader (if available)
3. Check focus indicators

**Expected Results**:
- [ ] All interactive elements are keyboard accessible
- [ ] Focus indicators are visible and clear
- [ ] Progress bar has proper ARIA attributes
- [ ] Button titles/labels are descriptive
- [ ] Component works with assistive technologies

## Bug Reporting

If any test fails or unexpected behavior is observed:

1. Note the specific test case and steps to reproduce
2. Record browser and OS information
3. Check browser console for any error messages
4. Document expected vs actual behavior
5. Take screenshots if visual issues are present

## Notes

- Some functionality may depend on the Rust backend being properly implemented
- Audio playback features require actual audio files and working audio system
- Network-related features may require proper API endpoints