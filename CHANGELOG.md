# alpha.0.0.5
## Additions:
- **Versioned JSON Configurations**
    > To reduce configuration breaking, data now may have a hidden version number that automatically will adapt older config versions to newer ones, as such no configurations have broken since alpha.0.0.5
- **Addon System**
    > Addons allow for certain functionality of Touchify to be seperated depending on the needs of a user, these addons are seperated into multiple extensions and utilize Touchify as a dependency to run. Features moved to addons include:
    > - Color Options Docker
    > - Brush Options Docker
    > - Reference Tabs Docker
    > - Compact Brush Toggler (New Arrival)
    >
    > Depending on an addon's importance or need, it may or may not be dropped in the future. Additionally, more extensions may become addons under the Touchify umbrella through this system in the future or even existing Touchify features themselves (like the Toolshelf Docker)
- **PropertyGrid / Settings Overhaul**
    > This includes:
    > - **Hint Text** - To provide additional information about what configuration variables do
    > - **Navigation Bar** - To provide the user an idea of where they are within the configuration files
    > - And many other smaller adjustments to the UI and logic
- **New Toolshelf Feature - Nested Toolshelf Sections**
    > - Allows you to nest a toolshelf within a section without having tabs, useful if you want two dockers in one section tab for instance.
- **New Popup Feature - Toolshelf Popups**
    > - Allows you to have your very own toolshelf-grade customizable popups.
- **New Popup Features**
    > These include the following:
    > - **Close Behavior** - Changes what causes the Popup to close
    > - **Popup Position** - Changes what the inital position of the popup is
    > - Toolshelf Actions can now optionally close the source popup on trigger (configurable through the actions themselves)
- **Shortcut Composer Compat Option for Toolshelf Actions**
    > - If a toolshelf action button has this option enabled, the action will be triggered on button press, and when you release the mouse or tablet stylus it will send the escape key to make it possible to use Shortcut Composer's features without any keyboard keys
- **New Scaling Options**
    > Various user interface elements managed by Touchify can now be scaled independently of their actual scale via configuration or hardcoded value using various scale multipliers found in the new "Preferences" section in Touchify's Settings
- **Experimental: Canvas Mouse Interaction Triggers**
    > Right, Left and Middle Mouse Clicks can now be setup to trigger krita actions when these events happen on the canvas. They do not override Krita's own Canvas Input Settings/Logic so be advised that there may be some overlap you'll have to disable (such as right click to open the Popup Palette)
## Bug Fixes / Improvements:
- **Various Configuration Reworks**
    > A number on numerous changes to improve consistency and reduce redundancy with the code that uses it
- **Better Popup Dialogs**
    > Reworked to iron out some oddities with scaling, performance and such
- **Toolshelf Sizing Optimization**
    > Automatic / Manual Size Adjustments should be far more reliable now
- **Improved Docker Containers**
    > Loading and Unloading of Dockers should now be far more consistent
- **Replaced all Timers with Central Timer**
    > Improves performance and scalability of the extension
## Planned Future Deprications:
- **Popup Types**
    > With the new addition of the Toolshelf Type for Popups, the existing modes now slightly redundant in terms of functionality they offer compared to toolshelfs. Existing functionality of Docker and Action Popups will be carried over in due time to Toolshelves
- **Toolshelf Docker**
    > With the arrival of popup toolshelfs, they could be adjusted to work as Dockers as well. This change will likely happen in due time
- **Docker Groups / Docker / Workspace Triggers**
    > Ideally, I'd like to consildate these legacy features to something better and more usable for the current system

# alpha.0.0.4

## Breaking Changes:
- **Configuration Format Change**
    > While I try to keep the configuration formats from breaking between each version, there are simply some changes that can't be done without breaking the last version's configuration files. Some may still work, but I recommend you back them up. The format will become more consistent once the alpha is over

## Additions:
- **Massive Refactoring** 
    > Lots of code consoldiation again, to make the code easier to follow for myself
- **New Popup Actions Feature - Close on Click**
    > Closes the Popup on Action Trigger when using a Actions Popup. Allows for behavior more in line with a context menu
- **New PropertyGrid / Settings Functionality - Duplicate List Items**
    > Need I say any more? You can now quickly duplicate any item in any configuration page!
- **New Toolshelf Feature - Presets**
    > You can now save and load toolshelf configurations on the fly, and select them from within a dropdown in the toolshelf itself
- **New Toolshelf Feature - Tabbed Section Customization**
    > Ethier have your tabbed view as tabs or a dropdown button
- **New Toolshelf Feature - Customizable Headers**
    > Toolshelf Headers now have far more customization to be suit whatever your needs may be
- **New On-Canvas Widgets Feature - Presets & Layout Editing**
    > On-Canvas Widgets are now fully layout driven and can be flexibily customized to fit whatever your needs may be
- **New Toolshelf Feature - Resizable Mode**
    > You can now resize the On-Canvas Toolshelfs if enabled through the new dropdown where you find the presets
- **New Toolshelf Feature - Brush Blending/Composite Selector**
    > You can now add a section to your toolshelf to manage your brush/layer blending options
- **New Toolshelf Feature - Layer Color Label Selector**
    > You can now add a section to your toolshelf to quickly modify the color label of any selected layers; Inspired by (https://github.com/LainFenrir/krita-label-box)
- **New Docker - Touchify Toolbox**
    > Combines ideas from the Toolkit Plugin and the Default Docker, it replaces the default toolbox in the On-Canvas widgets as well. It also features presets
- **New Docker - Reference Tabs**
    > Ported and Upgraded from the original Reference Tabs Docker (https://krita-artists.org/t/plugin-reference-tabs-docker/47732)
- **Theming Refresh**
    > Made some theming changes to hopefully better suit those who don't wish to use a dark theme. Never a perfect reload when switching between themes but at least it works better with any theme now. This will be an ongoing thing I continue to research
- **NtWidgetPad Improvements**
    > Now has the ability to be resized and has also undergone some massive refactoring for continued stability.
- **Universal Actions / Action System Change**
    > Massively reworked the entire action assignment system to allow for more flexibility and customization without restarting the entire application. This also allows you to do things with the Toolshelfs that previously required a registered action
- **Migrated Popups, Docker Groups, Docker Toggles, and Workspace Toggles to the Universal Actions System**
    > This means that these kinds of features can be constructed without reloading the application when used with a toolshelf.
## Bug Fixes:
- **Fixed some Linux related crashing issues**
    > Enough said
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



