# alpha.0.0.4

## Breaking Changes:
- **Configuration Format Change**
    > While I try to keep the configuration formats from breaking between each version, there are simply some changes that can't be done without breaking the last version's configuration files. Some may still work, but I recommend you back them up. The format will become more consistent once the alpha is over

## Additions:
- **Massive Refactoring** 
    > Lots of code consoldiation again, to make the code easier to follow for myself
- **New Docker - Touchify Toolbox**
    > Combines ideas from the Toolkit Plugin and the Default Docker, it replaces the default toolbox in the On-Canvas widgets as well.
- **Theming Refresh**
    > Made some theming changes to hopefully better suit those who don't wish to use a dark theme. Still not a perfect reload when switching between themes but at least it works better with a light theme now.
- **NtWidgetPad Improvements**
    > Now has the ability to be resized and has also undergone
- **Universal Actions / Action System Change**
    > Massively reworked the entire action assignment system to allow for more flexibility and customization without restarting the entire application. This also allows you to do things with the Toolshelfs that previously required a registered action
- **Migrated Popups, Docker Groups, Docker Toggles, and Workspace Toggles to the Universal Actions System**
    > This means that these kinds of features can be constructed without reloading the application when used with a toolshelf.

## Known Bugs:
- **Compatibility with Multiple Instances of Krita**
    > While it will not crash, there are currently some kinks I'm investigating related to some functionality. Help would be appreciated on this if you are a dev


# alpha.0.0.3

## Breaking Changes:
- **Configuration Format Change**
    > While I try to keep the configuration formats from breaking between each version, there are simply some changes that can't be done without breaking the last version's configuration files. Some may still work, but I recommend you back them up. The format will become more consistent once the alpha is over

## Additions:
- **Massive Refactoring** 
    > Lots of code consoldiation again, to make the code easier to follow for myself
- **Improved Hotkey Assignment**
    > Hotkeys now have their own dedicated configuration section with nice dropdowns of actions for you to choose from
- **Better Docker Sharing**
    > The Entire Concept of Borrowing Dockers has been overhauled, so you can now forcefully load dockers in places they were unloaded due to being loaded elsewhere
- **Compatibility with Multiple Instances of Krita**
    > No longer will the plugin have crashes if you try to use additional Krita windows
- **New Popup Container Type - Window**
    > Collapsable, Movable, Closable and Dragable. Useful if you want to have something like a window that but not tied to the dockable docker widgets or just something that can be temporarily hidden
- **New Toolshelf Feature - Pin Toolshelf Option**
    > Returning feature from KanvasBuddy, when not pinned, whatever page your Toolshelf is on when the Canvas is interacted with, will return to the main page, when pinned, it will stay in place
- **New Toolshelf Feature - Action Panels**
    > You can now have an additional set of actions within toolshelf pages, come with many diffrent features and options. You can now have as many actions as you want wherever you want inside toolshelfs!
- **New Toolshelf Feature - Brush Preset Actions**
    > Action Panels can now be used to switch to diffrent brush presets, allowing you to place and orginize your brushes however you see fit
- **New Toolshelf Feature - Customizable Frontpage**
    > Frontpages are now treated the same as normal pages, meaning anything you can do with subpages, you can do on the frontpages
- **New Toolshelf Feature - Multi-Column Support**
    > You can now place multiple sections in a single row, which could be dockers or action buttons
- **New Action - Popup Menu Bar**
    > When triggered a context menu will appear at the cursor with all of the actions avaliable in Krita's menu bar, useful if you are in canvas only mode and need that one niche thing you rarely use
- **Configuration Dialog Usability Improvements**
    > The Configuration Dialog no longer steals focus and prevents you interacting with Krita while it's open, additionally I've added an "Apply" button to apply changes without closing the dialog
- **Configuration Dialog Layout Improvements**
    > Certain Elements now are presented better with new logic and features added to the **PropertyGrid** component
- **Canvas Toolbox Improvement - Right Click Menu**
    > The toolbox's native right click context menu previously wasn't avaliable in the canvas version of the toolbox. Support for it has been added
- **New Docker - Brush Options**
    > Similar to the 4 Brush Option Sliders in the Toolbar, this docker replicates their functionality in the form of a docker
- **New Docker - Color Options**
    > Similar to the Color Picker in the Toolbar, this docker replicates it's functionality in the form of a docker
- **New Docker - Touchify Toolshelf**
    > Just like the On-Canvas Toolshelf Widgets, but now in the form of a Docker
- **New Feature - Canvas Decoration Presets**
    > Change Transparency Background Colors, Selection Overlays, and More with Presets!
- **And More...**
    > - Added an Action for "Configure Touchify..."
    > - Toolshelfs can now share the Page Buttons with other Panels besides just the Home Panel
    > - Added a WIP Privacy Mode to Hide Recent Documents
## Bug Fixes:
- **Popup Dockers Improvements** 
    > Various Bug Fixes and Other Backend Improvements
- **Tool Options Bug Fixes and Improvements**
    > No Longer will Tool Options have certain quirks that prevent it from being used in other ways
- **On-Canvas Widgets Bug Fixes**:
    > Improved Canvas Focus Detection for Pinned Mode
    > Addressed Widget Offset when Canvas Rulers are visible 
    > Workaround for the Scaled Lag when Pinned Mode is Off for On Canvas Widgets



