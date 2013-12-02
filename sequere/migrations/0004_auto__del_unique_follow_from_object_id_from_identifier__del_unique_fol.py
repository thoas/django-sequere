# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Removing unique constraint on 'Follow', fields ['to_object_id', 'to_identifier']
        db.delete_unique(u'sequere_follow', ['to_object_id', 'to_identifier'])

        # Removing unique constraint on 'Follow', fields ['from_object_id', 'from_identifier']
        db.delete_unique(u'sequere_follow', ['from_object_id', 'from_identifier'])


    def backwards(self, orm):
        # Adding unique constraint on 'Follow', fields ['from_object_id', 'from_identifier']
        db.create_unique(u'sequere_follow', ['from_object_id', 'from_identifier'])

        # Adding unique constraint on 'Follow', fields ['to_object_id', 'to_identifier']
        db.create_unique(u'sequere_follow', ['to_object_id', 'to_identifier'])


    models = {
        'sequere.follow': {
            'Meta': {'ordering': "['-created_at']", 'unique_together': "(('from_object_id', 'from_identifier', 'to_object_id', 'to_identifier'),)", 'object_name': 'Follow'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'from_identifier': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True'}),
            'from_object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_mutual': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'to_identifier': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True'}),
            'to_object_id': ('django.db.models.fields.PositiveIntegerField', [], {})
        }
    }

    complete_apps = ['sequere']