# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Follow.is_mutual'
        db.add_column(u'sequere_follow', 'is_mutual',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Follow.is_mutual'
        db.delete_column(u'sequere_follow', 'is_mutual')


    models = {
        'sequere.follow': {
            'Meta': {'ordering': "['-created_at']", 'unique_together': "(('from_object_id', 'from_identifier'), ('from_object_id', 'from_identifier', 'to_object_id', 'to_identifier'), ('to_object_id', 'to_identifier'))", 'object_name': 'Follow'},
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