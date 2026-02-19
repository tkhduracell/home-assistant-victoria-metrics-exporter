Render `custom_components/victoria_metrics/icon.svg` to PNG icon files for Home Assistant.

Steps:
1. Run `qlmanage -t -s 512 -o custom_components/victoria_metrics custom_components/victoria_metrics/icon.svg` to generate the 512px version
2. Rename the output from `icon.svg.png` to `icon@2x.png`
3. Run `qlmanage -t -s 256 -o custom_components/victoria_metrics custom_components/victoria_metrics/icon.svg` to generate the 256px version
4. Rename the output from `icon.svg.png` to `icon.png`
5. Show the generated `icon.png` to confirm it looks correct
