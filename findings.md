Findings, worst first:

1. HTML scraped with regex to find the cover image ( Article._FIRST_IMG_SRC_RE  /  cover_thumbnail_url  in  apps/articles/models.py ). Parsing HTML with regex is fragile (attribute order, quoting, self-closing variants) and couples  Article  to the private naming convention of  make_thumbnail  ( ..._thumb.jpg ) in a different app. A real HTML parser, or an explicit stored cover-image reference, would be more robust.

2. No relationship between  Article  and its inline images.  SummernoteAttachment  has no FK to the  Article / BoardPost  that uses it. Deleting an article never deletes its uploaded/compressed images or thumbnails — orphaned files accumulate in  media/  indefinitely.
IN PROGRESS ...

3. Copy-pasted  save()  override (compress → two separate  .update()  calls → make_thumbnail) duplicated verbatim across  PictureOfWeek ,  SummernoteAttachment  ( apps/home/models.py ) and  BoardImage  ( apps/board/models.py ). Violates DRY; a mixin or a single helper ( process_uploaded_image(instance, field_name) ) would remove ~15 duplicated lines ×3.

4. Two  UPDATE  queries instead of one in every one of those  save()  methods ( .update(image=...)  then  .update(thumbnail=...) ), plus the initial  INSERT  — 3 DB writes for what could be 2.

5. Image re-processing does redundant I/O:  compress_image  and  make_thumbnail  each independently call  Image.open(image_field.path)  (file read from disk twice), and the JPEG quality-reduction loop re-writes the file to disk up to 6 times per save instead of probing size in memory before one final write.

6. Storage abstraction leak:  compress_image  uses  os.rename(image_path, storage.path(new_name))  directly instead of the storage API, tying the code to local-filesystem storage only (breaks silently if  MEDIA  storage is ever swapped for S3/cloud storage).

7. Cross-app layering smell:  compress_image / make_thumbnail  are generic image utilities but live in  apps/home/models.py ;  apps/board/models.py  imports them from another app's models module. Belongs in a shared, app-agnostic module (e.g.  apps/common/images.py ).

8. No error handling around  Image.open . A non-image file with an image-like extension will raise an unhandled  PIL.UnidentifiedImageError  → 500, instead of a clean form/validation error.

9.  backfill_thumbnails  command omits  SummernoteAttachment  — only covers  BoardImage / PictureOfWeek , so any pre-existing inline article images without a thumbnail are never backfilled, despite the model having the same  thumbnail  field shape.

10. (minor) Double bleach sanitization:  SummernoteTextFormField.to_python  and  SummernoteTextField.to_python  both call  bleach.clean()  — harmless but redundant, worth a comment or removing the model-field duplication.
