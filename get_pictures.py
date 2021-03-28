def get(vk_session, session, image_url):
    attachments = []
    from vk_api import VkUpload

    upload = VkUpload(vk_session)
    image = session.get(image_url, stream=True)
    photo = upload.photo_messages(photos=image.raw)[0]
    attachments.append(
        'photo{}_{}'.format(photo['owner_id'], photo['id'])
    )
    attachment = ','.join(attachments)
    return attachment

