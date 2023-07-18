# Photo

Digital photography tools

## Dependencies

PIL, hachoir

## Organise

Re-organises a directory of photos, using the DateTimeOriginal EXIF tag.

- searches for image files recursively
- eliminates duplicate files (identical content, different name)
- creates year and month directories
- adds timestamp to filenames and moves them to year/month directory
- puts undated image files in a separate directory
