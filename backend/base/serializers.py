from rest_framework import serializers


class CustomAnalyticsSerializer(serializers.Serializer):
    """
    Serializer for custom analytics request input details.
    """
    age = serializers.IntegerField(required=False)
    ethnicity = serializers.CharField(required=False)
    tumor_grade = serializers.IntegerField(required=False)
    tumor_size = serializers.CharField(required=False)
    num_pos_nodes = serializers.CharField(required=False)
    er_status = serializers.CharField(required=False)
    pr_status = serializers.CharField(required=False)
    her2_status = serializers.CharField(required=False)
    type = serializers.CharField(required=False)
    tumor_number = serializers.CharField(required=False)


class DiagnosisSerializer(serializers.Serializer):
    """
    Serializer for diagnosis request input details.
    """
    age = serializers.IntegerField(required=True)
    tumor_size_in_mm = serializers.IntegerField(required=True)
    tumor_grade = serializers.IntegerField(required=True)
    er_status = serializers.CharField(required=True)
    pr_status = serializers.CharField(required=True)
    her2_status = serializers.CharField(required=True)
    num_pos_nodes = serializers.IntegerField(required=True)
    ethnicity = serializers.CharField(required=True)
    sex = serializers.CharField(required=False, default='Female')
    type = serializers.CharField(required=False)
    site = serializers.CharField(required=False)
    laterality = serializers.CharField(required=False)
    stage = serializers.CharField(required=False)
    number_of_tumors = serializers.IntegerField(required=True)
    region = serializers.CharField(required=True)


class DiagnosisDataSerializer(serializers.Serializer):
    age = serializers.IntegerField(required=True)
    tumor_size_in_mm = serializers.IntegerField(required=True)
    tumor_size_in_mm_sd = serializers.CharField(
        required=False)  # For similar diagnoses fuction
    tumor_grade = serializers.IntegerField(required=True)
    er_status = serializers.CharField(required=True)
    pr_status = serializers.CharField(required=True)
    her2_status = serializers.CharField(required=True)
    num_pos_nodes = serializers.IntegerField(required=True)
    ethnicity = serializers.CharField(required=True)
    sex = serializers.CharField(required=False, default='Female')
    type = serializers.CharField(required=False)
    site = serializers.CharField(required=False)
    laterality = serializers.CharField(required=False)
    stage = serializers.CharField(required=False)
    number_of_tumors = serializers.IntegerField(required=True)
    region = serializers.CharField(required=True)

    def validate(self, data):
        data = dict(data)
        if data.get('ethnicity') == 'Caucasian':
            data['ethnicity'] = 'White'
        elif data.get('ethnicity') == 'African American':
            data['ethnicity'] = 'Black'
        elif data.get('ethnicity') == 'Asian':
            data['ethnicity'] = 'Asian or Pacific Islander'
        elif data.get('ethnicity') == 'Other':
            data['ethnicity'] = 'Unknown'

        data['tumor_size_in_mm_sd'] = data.get('tumor_size_in_mm')
        if data.get('tumor_size_in_mm') >= 50:
            data['tumor_size_in_mm'] = ">5cm"
        elif data.get('tumor_size_in_mm') >= 30:
            data['tumor_size_in_mm'] = ">3cm"
        elif data.get('tumor_size_in_mm') >= 20:
            data['tumor_size_in_mm'] = "<3cm"
        elif data.get('tumor_size_in_mm') >= 10:
            data['tumor_size_in_mm'] = "<2cm"
        elif data.get('tumor_size_in_mm') < 10:
            data['tumor_size_in_mm'] = "<1cm"

        # 0.    1. Any tumor size, dcis or in situ, and No positive lymph nodes
        if data.get('tumor_size_in_mm') in ['<1cm', '<2cm', '<3cm',
                                            '>3cm', '>5cm'] \
                and data.get('num_pos_nodes') == '0' \
                and (data.get('type') == 'DCIS'
                     or data.get('region') == 'In Situ'):
            data['stage'] = '0'
        # I.    1. Tumor size <2cm and no positive nodes
        elif data.get('tumor_size_in_mm') == '<2cm' and \
                data.get('num_pos_nodes') == 0:
            data['stage'] = 'I'
        # IIA.  1. Tumor size <5cm and no positive nodes.
        #       2. Tumor size of <2cm and <3 positive nodes
        elif (data.get('tumor_size_in_mm') in ['<3cm', '>3cm']
              and data.get('num_pos_nodes') == '0') \
                or (data.get('tumor_size_in_mm') == '<2cm'
                    and data.get('num_pos_nodes') < 3):
            data['stage'] = 'IIA'
        # IIB.  1. Tumor size <5cm and <3 positive nodes
        #       2. Tumor size >5cm and no positive nodes
        elif (data.get('tumor_size_in_mm') in ['<3cm', '>3cm']
              and data.get('num_pos_nodes') < 3) \
                or (data.get('tumor_size_in_mm') == '>5cm'
                    and data.get('num_pos_nodes') == 0):
            data['stage'] = 'IIB'
        # IIIA. 1. Any tumor size and <9 positive nodes
        #       2. Tumor size >5cm and <3 nodes
        elif (data.get('tumor_size_in_mm') in ['<1cm', '<2cm', '<3cm',
                                               '>3cm', '>5cm']
              and data.get('num_pos_nodes') < 9) \
                or (data.get('tumor_size_in_mm') == '>5cm'
                    and data.get('num_pos_nodes') < 3):
            data['stage'] = 'III'
        # IIIB. 1. Any tumor size and IBC and <9 positive nodes
        elif data.get('tumor_size_in_mm') in ['<1cm', '<2cm', '<3cm',
                                              '>3cm', '>5cm'] \
                and data.get('type') == 'IBC' \
                and data.get('num_pos_nodes') < 9:
            data['stage'] = 'III'
        # IIIC. 1. >10 positive nodes and any tumor size
        elif data.get('tumor_size_in_mm') in ['<1cm', '<2cm', '<3cm',
                                              '>3cm', '>5cm'] \
                and data.get('num_pos_nodes') > 10:
            data['stage'] = 'III'
        # IV.   1. Regional - Distant
        elif data.get('region') == 'Distant':
            data['stage'] = 'IV'

        return data
