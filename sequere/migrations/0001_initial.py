# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Follow'
        db.create_table(u'sequere_follow', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('from_object_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('from_identifier', self.gf('django.db.models.fields.CharField')(max_length=50, db_index=True)),
            ('to_object_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('to_identifier', self.gf('django.db.models.fields.CharField')(max_length=50, db_index=True)),
        ))
        db.send_create_signal('sequere', ['Follow'])


    def backwards(self, orm):
        # Deleting model 'Follow'
        db.delete_table(u'sequere_follow')


    models = {
        'sequere.follow': {
            'Meta': {'ordering': "['-created_at']", 'object_name': 'Follow'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'from_identifier': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True'}),
            'from_object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'to_identifier': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True'}),
            'to_object_id': ('django.db.models.fields.PositiveIntegerField', [], {})
        }
    }

    complete_apps = ['sequere']