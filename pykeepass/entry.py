from baseelement import BaseElement
from copy import deepcopy
from lxml.etree import Element
import logging
import xmlfactory
import group


logger = logging.getLogger(__name__)


class Entry(BaseElement):

    def __init__(self, title=None, username=None, password=None, url=None,
                 notes=None, tags=None, expires=None, expiration=None,
                 icon=None, element=None):
        if element is None:
            element = Element('Entry')
            title = xmlfactory.create_title_element(title)
            uuid = xmlfactory.create_uuid_element()
            username = xmlfactory.create_username_element(username)
            password = xmlfactory.create_password_element(password)
            times = xmlfactory.create_times_element(expires, expiration)
            if url:
                url = xmlfactory.create_url_element(url)
                element.append(url)
            if notes:
                notes = xmlfactory.create_notes_element(notes)
                element.append(notes)
            if tags:
                tags = xmlfactory.create_tags_element(tags)
                element.append(tags)
            if icon:
                icon = xmlfactory.create_icon_element(icon)
                element.append(icon)
            element.append(title)
            element.append(uuid)
            element.append(username)
            element.append(password)
            element.append(times)

        self._element = element

    def __get_string_field(self, key):
        results = self._element.xpath('String/Key[text()="{}"]/../Value'.format(key))
        if results:
            return results[0].text

    def __set_string_field(self, key, value):
        results = self._element.xpath('String/Key[text()="{}"]/..'.format(key))
        if results:
            results[0].Value = value
        else:
            logger.debug('No field named {}. Create it.'.format(key))
            el = xmlfactory._create_string_element(key, value)
            self._element.append(el)

    # Name is just a shortcut for title, so that both the Entry and Group can
    # share the same path property implementation
    @property
    def name(self):
        return self.title

    @name.setter
    def name(self, value):
        self.title = value

    @property
    def title(self):
        return self.__get_string_field('Title')

    @title.setter
    def title(self, value):
        return self.__set_string_field('Title', value)

    @property
    def username(self):
        return self.__get_string_field('UserName')

    @username.setter
    def username(self, value):
        return self.__set_string_field('UserName', value)

    @property
    def password(self):
        return self.__get_string_field('Password')

    @password.setter
    def password(self, value):
        return self.__set_string_field('Password', value)

    @property
    def url(self):
        return self.__get_string_field('URL')

    @url.setter
    def url(self, value):
        return self.__set_string_field('URL', value)

    @property
    def notes(self):
        return self.__get_string_field('Notes')

    @notes.setter
    def notes(self, value):
        return self.__set_string_field('Notes', value)

    @property
    def icon(self):
        return self._get_subelement_text('IconID')

    @icon.setter
    def icon(self, value):
        return self._set_subelement_text('IconID', value)

    @property
    def tags(self):
        val =  self._get_subelement_text('Tags')
        return val.split(';') if val else val

    @tags.setter
    def tags(self, value):
        # Accept both str or list
        v = ';'.join(value if type(value) is list else [value])
        return self._set_subelement_text('Tags', v)

    def __get_times_property(self, prop):
        times = self._element.find('Times')
        if times is not None:
            prop = times.find(prop)
            if prop is not None:
                return prop.text

    @property
    def expires(self):
        d = self.__get_times_property('Expires')
        if d is not None:
            return d == 'True'

    @property
    def expiry_time(self):
        d = self.__get_times_property('ExpiryTime')
        if d is not None:
            return xmlfactory._date_from_str(d)

    @property
    def ctime(self):
        d = self.__get_times_property('CreationTime')
        if d is not None:
            return xmlfactory._date_from_str(d)

    @property
    def atime(self):
        d = self.__get_times_property('LastAccessTime')
        if d is not None:
            return xmlfactory._date_from_str(d)

    @property
    def mtime(self):
        d = self.__get_times_property('LastModificationTime')
        if d is not None:
            return xmlfactory._date_from_str(d)

    @property
    def history(self):
        if self._element.find('History') is not None:
            return [Entry(element=x) for x in self._element.find('History').findall('Entry')]

    @history.setter
    def history(self, value):
        raise NotImplementedError()

    @property
    def parentgroup(self):
        return group.Group(element=self._element.getparent())

    def touch(self, modify=False):
        '''
        Update last access time of an entry
        '''
        self._element.Times.LastAccessTime = xmlfactory._dateformat()
        if modify:
            self._element.Times.LastModificationTime = xmlfactory._dateformat()

    def save_history(self):
        '''
        Save the entry in its history
        '''
        archive = deepcopy(self._element)
        if self._element.find('History') is not None:
            archive.remove(archive.History)
            self._element.History.append(archive)
        else:
            history = Element('History')
            history.append(archive)
            self._element.append(history)

    def __str__(self):
        return 'Entry {}: {} at {}'.format(self.title, self.username, self.path)

    def __unicode__(self):
        return self.__str__()

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return (
            (self.title, self.username, self.password, self.url,
             self.notes, self.icon, self.tags, self.atime, self.ctime,
             self.mtime, self.expires, self.uuid) ==
            (other.title, other.username, other.password, other.url,
             other.notes, other.icon, other.tags, other.atime, other.ctime,
             other.mtime, other.expires, other.uuid)
        )