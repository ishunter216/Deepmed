import json

from django.conf import settings
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from base.serializers import DiagnosisSerializer
from lib.dataset import breast_cancer_by_grade, diagnosis, \
    percent_race_with_cancer_by_age, \
    breakout_by_stage, breast_cancer_by_size, \
    percent_of_women_with_cancer_by_race_overall, \
    distribution_of_stage_of_cancer, surgery_decisions, chemotherapy, \
    radiation, breast_cancer_by_state, \
    breast_cancer_at_a_glance, breast_cancer_by_age, \
    percent_women_annualy_diagnosed, percent_women_by_type, \
    breast_cancer_by_state2, breast_cancer_at_a_glance2


def v_get_t_size_cm(size_mm):
    t_size_cm = None
    if size_mm >= 50:
        t_size_cm = ">5cm"
    elif size_mm >= 30:
        t_size_cm = ">3cm"
    elif size_mm >= 20:
        t_size_cm = "<3cm"
    elif size_mm >= 10:
        t_size_cm = "<2cm"
    elif size_mm < 10:
        t_size_cm = "<1cm"

    return t_size_cm


class ReportDataView(GenericAPIView):
    serializer_class = DiagnosisSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        serializer = self.get_serializer(data=request.query_params)

        serializer.is_valid(raise_exception=True)
        dd = dict(serializer.validated_data)

        age = json.dumps({'age': dd.get('age')})

        ethnicity = dd.get('ethnicity')

        if ethnicity == 'Caucasian':
            v_ethnicity = 'White'
        elif ethnicity == 'African American':
            v_ethnicity = 'Black'
        elif ethnicity == 'Asian':
            v_ethnicity = 'Asian or Pacific Islander'
        elif ethnicity == 'Other':
            v_ethnicity = 'Unknown'
        else:
            v_ethnicity = ethnicity

        is_radiation_therapy = 'No'  # Radiation Therapy

        # Recommended Treatment Plans

        ## Overall Plans

        overall_plans = []
        hormonal_therapy = []
        radiation_therapy = []
        chemo_therapy = []

        try:
            import subprocess
            import ast
            import re
            regex = r"\((.*?)\)"

            # START SURGERY
            surgery_args = ','.join([dd.get('sex'),
                                     str(dd.get('age')),
                                     v_ethnicity,
                                     str(float(dd.get('tumor_grade', 'unk'))),
                                     dd.get('site'),
                                     dd.get('type'),
                                     dd.get('stage'),
                                     dd.get('region'),
                                     v_get_t_size_cm(
                                         dd.get('tumor_size_in_mm')),
                                     str(dd.get('number_of_tumors')),
                                     str(dd.get('num_pos_nodes'))])

            surgery_command_str = [settings.ML_PYTHON_PATH,
                                   settings.ML_COMMAND_FILE,
                                   surgery_args, 'Surgery']

            surgery_command = subprocess.Popen(surgery_command_str,
                                               stdout=subprocess.PIPE,
                                               stderr=subprocess.PIPE,
                                               cwd=settings.ML_COMMAND_DIR)
            surgery_output, err = surgery_command.communicate()

            # To-Do remove try-except
            try:
                surgery_response = ast.literal_eval(
                    re.search(regex,
                              str(surgery_output.decode('utf8'))).group())
            except:
                surgery_response = ()

            # END SURGERY

            # START CHEMO

            chemo_args = ','.join([
                str(dd.get('age')),
                v_ethnicity,
                str(float(dd.get('tumor_grade'))),
                dd.get('type'),
                dd.get('stage'),
                dd.get('region'),
                v_get_t_size_cm(dd.get('tumor_size_in_mm')),
                str(dd.get('number_of_tumors')),
                str(dd.get('num_pos_nodes')),
                str(dd.get('er_status')),
                str(dd.get('pr_status')),
                str(dd.get('her2_status'))])

            chemo_command_str = [settings.ML_PYTHON_PATH,
                                 settings.ML_COMMAND_FILE,
                                 chemo_args, 'Chemo']

            chemo_command = subprocess.Popen(chemo_command_str,
                                             stdout=subprocess.PIPE,
                                             stderr=subprocess.PIPE,
                                             cwd=settings.ML_COMMAND_DIR)
            chemo_output, err = chemo_command.communicate()

            chemo_response = ast.literal_eval(
                re.search(regex, str(chemo_output.decode('utf8'))).group())

            # END CHEMO

            # START RADIATION

            import copy

            radiation_args = [
                str(dd.get('age')),
                v_ethnicity,
                str(float(dd.get('tumor_grade'))),
                dd.get('site'),
                dd.get('type'),
                dd.get('stage'),
                dd.get('region'),
                v_get_t_size_cm(dd.get('tumor_size_in_mm')),
                str(dd.get('number_of_tumors')),
                str(dd.get('num_pos_nodes')),
                str(dd.get('er_status')),
                str(dd.get('pr_status')),
                str(dd.get('her2_status'))]

            sm_radiation_args = copy.deepcopy(
                radiation_args)  # Copy base list of args

            sm_radiation_args.append('Mastectomy')
            sm_radiation_args.append(chemo_response[0])

            sm_radiation_command_str = [settings.ML_PYTHON_PATH,
                                        settings.ML_COMMAND_FILE,
                                        ','.join(sm_radiation_args),
                                        'Radiation']

            sm_radiation_command = subprocess.Popen(sm_radiation_command_str,
                                                    stdout=subprocess.PIPE,
                                                    stderr=subprocess.PIPE,
                                                    cwd=settings.ML_COMMAND_DIR)

            sm_radiation_output, err = sm_radiation_command.communicate()

            sm_radiation_response = ast.literal_eval(
                re.search(regex,
                          str(sm_radiation_output.decode('utf8'))).group())

            sl_radiation_args = copy.deepcopy(
                radiation_args)  # Copy base list of args

            sl_radiation_args.append('Lumpectomy')
            sl_radiation_args.append(chemo_response[0])

            sl_radiation_command_str = [settings.ML_PYTHON_PATH,
                                        settings.ML_COMMAND_FILE,
                                        ','.join(sm_radiation_args),
                                        'Radiation']

            sl_radiation_command = subprocess.Popen(sl_radiation_command_str,
                                                    stdout=subprocess.PIPE,
                                                    stderr=subprocess.PIPE,
                                                    cwd=settings.ML_COMMAND_DIR)
            sl_radiation_output, err = sl_radiation_command.communicate()

            sl_radiation_response = ast.literal_eval(
                re.search(regex,
                          str(sl_radiation_output.decode('utf8'))).group())

            # END RADIATION

            overall_plans = []

            surgery_level = round(surgery_response[1] * 100)
            chemo_level = round(chemo_response[1] * 100)
            sm_radiation_level = round(sm_radiation_response[1] * 100)
            sl_radiation_level = round(sl_radiation_response[1] * 100)

            if surgery_response[0] == 'Mastectomy':
                is_radiation_therapy = sm_radiation_response[0]
                overall_plans.append({
                    'name': 'Preferred Outcome A',
                    'type': surgery_response[0],
                    'radiation': 'Y' if sm_radiation_response[
                                            0] == 'Yes' else 'N',
                    'radiation_confidence_level': sm_radiation_level,
                    'chemo': 'Y' if chemo_response[0] == 'Yes' else 'N',
                    'chemo_confidence_level': chemo_level,
                    'surgery': 'Y',
                    'surgery_confidence_level': surgery_level,
                    'level': surgery_level})
                overall_plans.append({
                    'name': 'Preferred Outcome B',
                    'type': 'Lumpectomy',
                    'radiation': 'Y' if sl_radiation_response[
                                            0] == 'Yes' else 'N',
                    'radiation_confidence_level': sl_radiation_level,
                    'chemo': 'Y' if chemo_response[0] == 'Yes' else 'N',
                    'chemo_confidence_level': chemo_level,
                    'surgery': 'Y',
                    'surgery_confidence_level': 100 - surgery_level,
                    'level': 100 - surgery_level})
            else:
                is_radiation_therapy = sl_radiation_response[0]
                overall_plans.append({
                    'name': 'Preferred Outcome A',
                    'type': surgery_response[0],
                    'radiation': 'Y' if sl_radiation_response[
                                            0] == 'Yes' else 'N',
                    'radiation_confidence_level': sl_radiation_level,
                    'chemo': 'Y' if chemo_response[0] == 'Yes' else 'N',
                    'chemo_confidence_level': chemo_level,
                    'surgery_confidence_level': surgery_level,
                    'surgery': 'Y',
                    'level': surgery_level})
                overall_plans.append({
                    'name': 'Preferred Outcome B',
                    'type': 'Mastectomy',
                    'radiation': 'Y' if sm_radiation_response[
                                            0] == 'Yes' else 'N',
                    'radiation_confidence_level': sm_radiation_level,
                    'chemo': 'Y' if chemo_response[0] == 'Yes' else 'N',
                    'chemo_confidence_level': chemo_level,
                    'surgery_confidence_level': 100 - surgery_level,
                    'surgery': 'Y',
                    'level': 100 - surgery_level})

            # Hormonal Therapy

            if dd.get('her2_status') == '+' or dd.get('er_status') == '+':
                hormonal_therapy.append({'name': 'Tamoxifen',
                                         'number_of_treatments': 120,
                                         'administration': 'Monthly'})

            # Radiation Therapy

            if is_radiation_therapy == 'Yes':
                radiation_therapy.append({'name': 'Beam Radiation',
                                          'number_of_treatments': 30,
                                          'administration': 'Daily'})

            # Chemo Therapy

            if chemo_response[0] == 'Yes' and \
                    int(dd.get('tumor_size_in_mm')) > 20 and \
                    dd.get('her2_status') != '+':
                chemo_therapy.append({
                    'plan': 'AC+T',
                    'number_of_treatments': [
                        {'name': 'A)', 'value': '4AC, 4T'},
                        {'name': 'B)', 'value': '4AC, 12T'}],
                    'administration': [
                        {'name': 'A)', 'values': [
                            {'name': 'AC', 'time': 'Every 2 weeks'},
                            {'name': 'T', 'time': 'Every 2 weeks'}
                        ]},
                        {'name': 'B)', 'values': [
                            {'name': 'AC', 'time': 'Every 2 weeks'},
                            {'name': 'T', 'time': 'Every week'}
                        ]}
                    ]
                })
            elif chemo_response[0] == 'Yes' and \
                    int(dd.get('tumor_size_in_mm')) < 20 and \
                    dd.get('her2_status') != '+':
                chemo_therapy.append({
                    'plan': 'C+T',
                    'number_of_treatments': [
                        {'name': 'A)', 'value': '4C, 4T'},
                        {'name': 'B)', 'value': '4C, 12T'}],
                    'administration': [
                        {'name': 'A)', 'values': [
                            {'name': 'C', 'time': 'Every 2 weeks'},
                            {'name': 'T', 'time': 'Every 2 weeks'}
                        ]},
                        {'name': 'B)', 'values': [
                            {'name': 'C', 'time': 'Every 2 weeks'},
                            {'name': 'T', 'time': 'Every week'}
                        ]}
                    ]
                })
            elif chemo_response[0] == 'Yes' and \
                    int(dd.get('tumor_size_in_mm')) > 20 and \
                    dd.get('her2_status') == '+':
                chemo_therapy.append({
                    'plan': 'AC+T+HCP',
                    'number_of_treatments': [
                        {'name': 'A)', 'value': '4AC, 4T, 52HCP'},
                        {'name': 'B)', 'value': '4AC, 12T, 52HCP'}],
                    'administration': [
                        {'name': 'A)', 'values': [
                            {'name': 'AC', 'time': 'Every 2 weeks'},
                            {'name': 'T', 'time': 'Every 2 weeks'},
                            {'name': 'HCP', 'time': 'Every week'}
                        ]},
                        {'name': 'B)', 'values': [
                            {'name': 'AC', 'time': 'Every 2 weeks'},
                            {'name': 'T', 'time': 'Every week'},
                            {'name': 'HCP', 'time': 'Every week'}
                        ]}
                    ]
                })
            elif chemo_response[0] == 'Yes' and \
                    int(dd.get('tumor_size_in_mm')) < 20 and \
                    dd.get('her2_status') == '+':
                chemo_therapy.append({
                    'plan': 'A+T+HCP',
                    'number_of_treatments': [
                        {'name': 'A)', 'value': '4C, 4T, 52HCP'},
                        {'name': 'B)', 'value': '4C, 12T, 52HCP'}],
                    'administration': [
                        {'name': 'A)', 'values': [
                            {'name': 'A', 'time': 'Every 2 weeks'},
                            {'name': 'T', 'time': 'Every 2 weeks'},
                            {'name': 'HCP', 'time': 'Every week'}
                        ]},
                        {'name': 'B)', 'values': [
                            {'name': 'A', 'time': 'Every 2 weeks'},
                            {'name': 'T', 'time': 'Every week'},
                            {'name': 'HCP', 'time': 'Every week'}
                        ]}
                    ]
                })

        except Exception as e:
            overall_plans = []
            hormonal_therapy = []
            radiation_therapy = []
            chemo_therapy = []

        data = {
            'recommended_treatment_plans': {
                'overall_plans': overall_plans,
                'hormonal_therapy': hormonal_therapy,
                'radiation_therapy': radiation_therapy,
                'chemo_therapy': chemo_therapy
            },
            'percent_women_by_type': percent_women_by_type(),
            'breast_cancer_by_grade_and_size': {
                'grade': breast_cancer_by_grade(age),
                'size': breast_cancer_by_size(age)
            },
            'distribution_of_stage_of_cancer': {
                'overall': distribution_of_stage_of_cancer(age),
                'by_race':
                    distribution_of_stage_of_cancer(
                        json.dumps({'age': dd.get('age'),
                                    'ethnicity': v_ethnicity},
                                   ensure_ascii=False)),
            },
            'percent_of_women_with_cancer_by_race': {
                'overall': percent_of_women_with_cancer_by_race_overall()
            },
            'surgery_decisions': surgery_decisions(age),
            'chemotherapy': {
                'overall': chemotherapy(age),
            },
            'radiation': {
                'overall': radiation(age),
            },
            'breast_cancer_by_state': breast_cancer_by_state2(1),
            'breast_cancer_at_a_glance': breast_cancer_at_a_glance2(),
            'breast_cancer_by_age': breast_cancer_by_age(),
        }

        data['chemotherapy']['breakout_by_stage'] = breakout_by_stage(
            json.dumps({
                'age': dd.get('age'),
                'chemo': 'Yes',
                "breast-adjusted-ajcc-6th-stage-1988": {
                    "$in": ["I", "IIA", "IIB", "IIIA",
                            "IIIB", "IIIC", "IIINOS", "IV",
                            0]
                }}, ensure_ascii=False))

        data['radiation']['breakout_by_stage'] = breakout_by_stage(json.dumps({
            'age': dd.get('age'),
            'radiation': 'Yes',
            "breast-adjusted-ajcc-6th-stage-1988": {
                "$in": ["I", "IIA", "IIB", "IIIA",
                        "IIIB", "IIIC", "IIINOS", "IV",
                        0]
            }}, ensure_ascii=False))

        data['percent_of_women_with_cancer_by_race'][
            'by_age'] = percent_race_with_cancer_by_age(json.dumps({
            'age': dd.get('age'),
            'sex': 'Female'
        }, ensure_ascii=False))

        dd.pop('laterality', None)
        dd.pop('site', None)
        dd.pop('type', None)
        dd.pop('stage', None)
        dd.pop('number_of_tumors', None)
        dd.pop('region', None)

        similar_diagnosis = diagnosis(json.dumps(dd, ensure_ascii=False),
                                      limit=20)

        if len(similar_diagnosis) < 20:
            dd.pop('race', None)
            similar_diagnosis = diagnosis(
                json.dumps(dd, ensure_ascii=False), limit=20)

            if len(similar_diagnosis) < 20:
                dd.pop('age', None)
                similar_diagnosis = diagnosis(
                    json.dumps(dd, ensure_ascii=False), limit=20)

        data['similar_diagnosis'] = similar_diagnosis

        return Response(data, status=status.HTTP_200_OK)


class ChartOneView(GenericAPIView):
    serializer_class = DiagnosisSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        serializer = self.get_serializer(data=request.query_params)

        serializer.is_valid(raise_exception=True)
        dd = dict(serializer.validated_data)

        age = json.dumps({'age': dd.get('age')})
        data = {
            'percent_women_annualy_diagnosed': percent_women_annualy_diagnosed(
                age),
        }
        return Response(data, status=status.HTTP_200_OK)


class ResourcesView(GenericAPIView):
    serializer_class = DiagnosisSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        serializer = self.get_serializer(data=request.query_params)

        serializer.is_valid(raise_exception=True)
        dd = dict(serializer.validated_data)

        if dd.get('er_status') == '+' and dd.get('pr_status') == '+' \
                and dd.get('her2_status') == '+':
            data = {
                "google_links": [
                    {
                        "link": "https://www.sciencedirect.com/science/article/pii/S0305737214002102",
                        "title": "Triple positive breast cancer: A distinct subtype?",
                        "description": "Triple positive breast cancer: A distinct subtype? - ScienceDirect"
                    },
                    {
                        "link": "https://www.cbcn.ca/en/blog/our-stories/trishamourot",
                        "title": "Facing triple positive breast cancer, Our Voices Blog – CBCN",
                        "description": "My life changed forever once I received the phone call no one wants to get early one morning in March 2015."
                    },
                    {
                        "link": "http://www.onclive.com/peer-exchange/questions-and-controversies-in-breast-cancer/triplepositive-metastatic-breast-cancer",
                        "title": "Triple-Positive Metastatic Breast Cancer",
                        "description": "Panelists Adam M. Brufsky, MD, PhD; Kimberly L. Blackwell, MD; Debu Tripathy, MD; José Baselga, MD, PhD; Denise A. Yardley, MD; and Carlos L. Arteaga, MD, discuss using chemotherapy and HER2 monoclonal antibodies to treat triple-positive metastatic breast cancer and their personal approaches."
                    },
                    {
                        "link": "https://www.curetoday.com/publications/cure/2017/breast-2017/piling-on-drugs-to-treat-her2positive-breast-cancer",
                        "title": "Piling on Drugs to Treat HER2-Positive Breast Cancer",
                        "description": "Piling on Drugs to Treat HER2-Positive Breast Cancer"
                    },
                    {
                        "link": "https://www.medicalnewstoday.com/articles/316789.php",
                        "title": "HER2-positive breast cancer: Causes, symptoms, and statistics",
                        "description": "The HER2 gene ordinarily makes proteins in the breast. When HER2 is abnormal, it causes a fast and aggressive type of breast cancer."
                    },
                    {
                        "link": "http://www.practiceupdate.com/content/increased-survival-in-patients-with-triple-positive-metastatic-breast-cancer-treated-with-trastuzumab/54715",
                        "title": " BLOCK | PracticeUpdate",
                        "description": "Increased Survival in Patients With Triple-Positive Metastatic Breast Cancer Treated With Trastuzumab"
                    },
                    {
                        "link": "https://www.verywell.com/triple-positive-breast-cancer-4151805",
                        "title": "Triple Positive Breast Cancer: When Your Tumor Is ER+, PG+, and HER2+",
                        "description": "What is the definition of triple positive breast cancer? How are tumors that are positive for HER2, ER, and PgR different and how are they treated?"
                    },
                    {
                        "link": "https://www.webmd.boots.com/breast-cancer/guide/types-er-positive-her2-positive",
                        "title": "Breast cancer types: ER positive, HER2 positive, triple negative",
                        "description": "Diagnosing the type of breast cancer a woman has is important for doctors when choosing the treatment approach."
                    },
                    {
                        "link": "https://www.futuremedicine.com/doi/full/10.2217/bmt-2017-0012",
                        "title": "Fulvestrant in breast cancer: also a good option in triple-positive breast cancer | Breast Cancer Management",
                        "description": "Fulvestrant in breast cancer: also a good option in triple-positive breast cancer | Breast Cancer Management"
                    },
                    {
                        "link": "https://rethinkbreastcancer.com/tag/triple-positive/",
                        "title": "Triple positive | Rethink Breast Cancer",
                        "description": "Triple positive | Rethink Breast Cancer"
                    }
                ],
                "blogs_and_posts": [
                    {
                        "link": "https://community.breastcancer.org/forum/80/topics/852383",
                        "title": "Breast Cancer Topic: Triple positive and concerned for recurrence and metastasis",
                        "description": "Breast Cancer Discussion Forums - Access the shared knowledge of thousands of people affected by breast cancer"
                    },
                    {
                        "link": "https://community.macmillan.org.uk/cancer_types/breast-cancer/f/38/t/92558",
                        "title": "Triple positive - is chemo necessary? - Breast cancer - Discussion Forum - Breast cancer - Macmillan's Online Community",
                        "description": "Triple positive - is chemo necessary? - Breast cancer - Discussion Forum - Breast cancer - Macmillan's Online Community"
                    },
                    {
                        "link": "https://www.youcaring.com/help-a-neighbor/life-as-a-24-year-old-battling-triple-positive-breast-cancer/146284",
                        "title": "Life as a 24 year old battling Triple Positive Breast Cancer | Neighbors & Community - YouCaring",
                        "description": "In October 2013, Danielle was diagnosed with a very aggressive form of Breast Cancer. Fighting Triple Positive breast cancer with the Her2 Gene. This cancer has taken a tremendous toll on Danielle and her Family. Cyndi, Danielle's mother is the only working source of income at this time for their..."
                    },
                    {
                        "link": "https://every-little-thingblog.com/tag/triple-positive-breast-cancer/",
                        "title": "triple positive breast cancer | Team Buna",
                        "description": "Posts about triple positive breast cancer written by teambuna"
                    },
                    {
                        "link": "http://her2support.org/vbulletin/showthread.php?t=23495",
                        "title": " Triple positive-Always a recurrance? - HER2 Support Group Forums",
                        "description": " Triple positive-Always a recurrance? her2group"
                    },
                    {
                        "link": "https://www.cbcn.ca/en/blog/our-stories/trishamourot",
                        "title": "Facing triple positive breast cancer, Our Voices Blog – CBCN",
                        "description": "My life changed forever once I received the phone call no one wants to get early one morning in March 2015."
                    },
                    {
                        "link": "https://www.sharecancersupport.org/2008/04/megan-her2-positive-breast-cancer/",
                        "title": "Megan: Her2-Positive Breast Cancer - Breast Cancer Stories",
                        "description": "When women call the SHARE helpline and tell me they've just been diagnosed with HER2-positive breast cancer, I know how scared they are. Often they've..."
                    },
                    {
                        "link": "http://stageivnowwhat.blogspot.com/p/blogs-i-follow.html",
                        "title": "The Cancer Classroom: Blogs I Follow",
                        "description": "Breast Cancer kills 1,430 people in the world daily; 113 die in the USA. Note: If you would like your blog added to this list, send me an"
                    },
                    {
                        "link": "http://blog.dana-farber.org/insight/2017/03/eric-winer-breast-cancer-treatment-yesterday-and-tomorrow-a-long-and-winding-road/",
                        "title": "Breast Cancer Treatment: Looking Back and Moving Forward",
                        "description": "As we look ahead there are three areas that need focus in breast cancer treatment: resistance to treatment, overtreatment, and health equity."
                    }
                ],
                "pubmed": [
                    {
                        "link": "https://www.ncbi.nlm.nih.gov/pubmed/28523293",
                        "title": "\"Triple positive\" breast cancer - a novel category?  - PubMed - NCBI",
                        "description": "Rom J Morphol Embryol. 2017;58(1):21-26. Multicenter Study; Review"
                    },
                    {
                        "link": "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4951261/",
                        "title": "“Triple positive” early breast cancer: an observational multicenter retrospective analysis of outcome",
                        "description": "We recently found that trastuzumab benefit may be lower in a small subset of early breast cancer (BC) patients (pts) with tumors expressing high levels of both hormonal receptors (HRs), i.e. triple positive (TP). To better investigate the role of HRs"
                    },
                    {
                        "link": "https://www.ncbi.nlm.nih.gov/pubmed/25554445",
                        "title": "Triple positive breast cancer: a distinct subtype?  - PubMed - NCBI",
                        "description": "Cancer Treat Rev. 2015 Feb;41(2):69-76. doi: 10.1016/j.ctrv.2014.12.005. Epub  2014 Dec 19. Review"
                    },
                    {
                        "link": "https://www.ncbi.nlm.nih.gov/pubmed/27644638",
                        "title": "Survival of Triple Negative versus Triple Positive Breast Cancers: Comparison and Contrast.  - PubMed - NCBI",
                        "description": "Asian Pac J Cancer Prev. 2016;17(8):3911-6. Comparative Study"
                    },
                    {
                        "link": "https://www.ncbi.nlm.nih.gov/pubmed/23278394",
                        "title": "Treatment of estrogen receptor-positive breast cancer.  - PubMed - NCBI",
                        "description": "Curr Med Chem. 2013;20(5):596-604."
                    },
                    {
                        "link": "https://www.ncbi.nlm.nih.gov/pubmed/26910921",
                        "title": "\"Triple positive\" early breast cancer: an observational multicenter retrospective analysis of outcome.  - PubMed - NCBI",
                        "description": "Oncotarget. 2016 Apr 5;7(14):17932-44. doi: 10.18632/oncotarget.7480. Multicenter Study; Observational Study; Research Support, Non-U.S. Gov't"
                    },
                    {
                        "link": "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4742168/",
                        "title": "Opposite regulation of MDM2 and MDMX expression in acquisition of mesenchymal phenotype in benign and cancer cells",
                        "description": "Plasticity of cancer cells, manifested by transitions between epithelial and mesenchymal phenotypes, represents a challenging issue in the treatment of neoplasias. Both epithelial-mesenchymal transition (EMT) and mesenchymal-epithelial transition (MET)"
                    },
                    {
                        "link": "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4961053/",
                        "title": "Relevance of Pathological Complete Response after Neoadjuvant Therapy for Breast Cancer",
                        "description": "Breast cancer is a heterogeneous disease, and the different biological subtypes have different prognostic impacts. Neoadjuvant trials have recently become popular as they offer several advantages compared to traditional adjuvant trials. Studies have shown"
                    },
                    {
                        "link": "https://www.ncbi.nlm.nih.gov/pubmed/29182983",
                        "title": "Mammospheres of hormonal receptor positive breast cancer diverge to triple-negative phenotype.  - PubMed - NCBI",
                        "description": "Breast. 2017 Nov 25;38:22-29. doi: 10.1016/j.breast.2017.11.009. [Epub ahead of print]"
                    },
                    {
                        "link": "https://www.ncbi.nlm.nih.gov/pubmed/29019331",
                        "title": "Clinical and Pathological Characteristics of Triple Positive Breast Cancer among Iraqi Patients.  - PubMed - NCBI",
                        "description": "Gulf J Oncolog. 2017 Sep;1(25):51-60."
                    }
                ],
                "news_articles": [
                    {
                        "link": "https://my.clevelandclinic.org/patient-stories/20-mother-overcomes-triple-positive-breast-cancer-diagnosis",
                        "title": "Mauriel Davis: Breast Cancer Patient Story | Cleveland Clinic",
                        "description": "Learn how Mauriel Davis, diagnosed with an aggressive form of Breast Cancer, overcame her illness after successful treatment at Cleveland Clinic."
                    },
                    {
                        "link": "https://www.cancertherapyadvisor.com/breast-cancer/breast-cancer-triple-blockade-her2-treatment-effective/article/735936/",
                        "title": "Triple Blockade May Be Effective in HER2-positive/ER-positive Breast Cancer - Cancer Therapy Advisor",
                        "description": "Objective response was noted in 95% of patients prior to surgery; 27% of patients had a pathological complete response in the breast and axillary nodes. "
                    },
                    {
                        "link": "https://www.nytimes.com/interactive/projects/well/breast-cancer-stories/stories/487",
                        "title": "Faces of Breast Cancer: Martha- Faces of Breast Cancer - Well - NYTimes.com",
                        "description": "My experience with (triple positive) breast cancer has taught me that you can handle so much more than you think is humanly possible."
                    },
                    {
                        "link": "https://breastcancer-news.com/2017/01/18/tucatinib-ont-380-seen-to-benefit-women-with-heavily-treated-breast-cancer/",
                        "title": "HER2-Positive Breast Cancer Seen to Respond Well to Investigational Therapy, Tucatinib",
                        "description": "A Phase 1 clinical trial shows women with heavily treated breast cancer could benefit from the investigational HER2 small molecule inhibitor tucatinib."
                    },
                    {
                        "link": "https://www.washingtonpost.com/news/to-your-health/wp/2018/02/01/breast-cancer-treatments-can-raise-risk-of-heart-disease-american-heart-association-warns/",
                        "title": "Breast cancer treatments can raise risk of heart disease, American Heart Association warns - The Washington Post",
                        "description": "A major new report says that patients should be monitored closely for cardiac toxicity"
                    },
                    {
                        "link": "https://medicalxpress.com/news/2018-02-insight-chromatin-therapies-breast-cancer.html",
                        "title": "Insight into chromatin therapies for breast cancer could aid personalized medicine",
                        "description": "Most traditional chemotherapy for cancer has dangerous side effects, but new research is finding ways to develop 'targeted agents' that reduce the side effects and are better tailored to individual patient needs. While these"
                    },
                    {
                        "link": "https://www.medicalnewstoday.com/articles/320762.php",
                        "title": "Fish-derived omega-3 best for preventing breast cancer",
                        "description": "Compared with the plant-based omega-3 ALA, EPA and DHA — which come from fatty fish — are much better for preventing breast cancer, researchers suggest."
                    },
                    {
                        "link": "https://www.healio.com/hematology-oncology/breast-cancer/news/print/hemonc-today/%7Ba433cfe0-6270-4a3d-bac2-f86edfa7aad5%7D/best-treatment-for-small-her-2positive-node-negative-breast-cancers-unknown",
                        "title": "Best treatment for small HER-2–positive, node-negative breast cancers unknown",
                        "description": "Hemonc Today | About 25% of breast cancers diagnosed in the United States areHER-2&#150;positive. Research has established that the HER-2 phenotypeis associated with poor DFS and OS.   Despite this increased risk, most women with HER-2&#150;positivenode-positive breast cancer and node-negative tumors larger than 1 cm have anestablished and effective treatment method with the use of "
                    },
                    {
                        "link": "https://www.themednet.org/what-is-your-preferred-regimen-for-triple-positive-breast-cancer-with-bone-only-recurrence",
                        "title": "theMednet - What is your preferred regimen for triple positive breast cancer with bone only recurrence? ",
                        "description": "theMednet - What is your preferred regimen for triple positive breast cancer with bone only recurrence? "
                    },
                    {
                        "link": "https://www.bcm.edu/healthcare/care-centers/breast-care-center/news-events/newsletters/new-treatment-options-horizon-her2-positive",
                        "title": "New treatment options on the horizon for HER2-positive breast cancer patients | Healthcare | Baylor College of Medicine | Houston, Texas",
                        "description": "Lester and Sue Smith Breast Center Newsletter - June 2012"
                    }
                ]
            }
        elif dd.get('er_status') == '-' and dd.get('pr_status') == '-' \
                and dd.get('her2_status') == '-':
            data = {
                "google_links": [
                    {
                        "link": "http://www.nationalbreastcancer.org/triple-negative-breast-cancer",
                        "title": "Triple Negative Breast Cancer - National Breast Cancer Foundation",
                        "description": "What is triple negative breast cancer? Who is at risk? Why is it so difficult to treat, and how can you treat it?"
                    },
                    {
                        "link": "https://en.wikipedia.org/wiki/Triple-negative_breast_cancer",
                        "title": "Triple-negative breast cancer",
                        "description": "Triple-negative breast cancer - Wikipedia"
                    },
                    {
                        "link": "https://ww5.komen.org/uploadedFiles/_Komen/Content/About_Breast_Cancer/Tools_and_Resources/Fact_Sheets_and_Breast_Self_Awareness_Cards/Triple%20Negative%20Breast%20Cancer.pdf",
                        "title": "Susan G. Komen | Triple Negative Breast Cancer",
                        "description": "Susan G. Komen | Triple Negative Breast Cancer | PDF"
                    },
                    {
                        "link": "https://www.medicalnewstoday.com/articles/319240.php",
                        "title": "Triple-negative breast cancer: What you need to know",
                        "description": "Triple-negative breast cancer is an aggressive type of cancer that is difficult to treat. Learn about risk factors, how it is diagnosed, and treatments."
                    },
                    {
                        "link": "https://www.webmd.com/breast-cancer/triple-negative-breast-cancer",
                        "title": "Triple-Negative Breast Cancer: Causes, Symptoms and Treatment",
                        "description": "Triple-negative breast cancer is a rare type. It’s serious, but it responds well if you catch it early. WebMD has details on the causes, symptoms, and treatments."
                    },
                    {
                        "link": "https://tnbcfoundation.org/understanding-triple-negative-breast-cancer/",
                        "title": "Understanding Triple Negative Breast Cancer",
                        "description": "Understanding Triple Negative Breast Cancer"
                    },
                    {
                        "link": "https://www.mdanderson.org/publications/cancerwise/2015/04/triple-negative-breast-cancer-5-things-you-should-know.html",
                        "title": "Triple-negative breast cancer: 5 things you should know | MD AndersonCancer Center",
                        "description": "We recently spoke with Naoto T. Ueno, M.D., Ph.D., section chief of Translational Breast Cancer Research in Breast Medical Oncology, to better understand triple-negative breast cancer (TNBC). Here's what he had to say."
                    },
                    {
                        "link": "https://www.healthline.com/health/triple-negative-breast-cancer-outlook-survival-rates-stage",
                        "title": "Triple Negative Breast Cancer Outlook: Survival Rates",
                        "description": "Learn about the outlook for triple negative breast cancer (TNBC)."
                    },
                    {
                        "link": "https://www.hopkinsmedicine.org/breast_center/breast_cancers_other_conditions/triple_negative_breast_cancer.html",
                        "title": "Triple Negative Breast Cancer Diagnosis & Treatment: Johns Hopkins Breast Center",
                        "description": "The Johns Hopkins Breast Center in Baltimore, MD, has breast cancer specialists who are experienced with the diagnosis and treatment of triple negative breast cancer."
                    },
                    {
                        "link": "https://www.sciencedaily.com/releases/2018/02/180208084816.htm",
                        "title": "How cancer stem cells drive triple-negative breast cancer -- ScienceDaily",
                        "description": "Researchers have new findings on a new stem cell pathway that allows a highly aggressive form of breast cancer -- triple-negative breast cancer -- to thrive"
                    }
                ],
                "blogs_and_posts": [
                    {
                        "link": "http://www.breastcancer.org/community/acknowledging/triple-negative",
                        "title": "Members Share Their Experiences With Triple-Negative Breast Cancer | Breastcancer.org",
                        "description": "Members Share Their Experiences With Triple-Negative Breast Cancer | Breastcancer.org"
                    },
                    {
                        "link": "http://www.lbbc.org/diagnosed-triple-negative-breast-cancer",
                        "title": "Triple-Negative Breast Cancer | Peer Support | Living Beyond Breast Cancer",
                        "description": "If you have been diagnosed with triple-negative breast cancer, it is normal to feel scared and have many questions about your diagnosis. Receive help here!"
                    },
                    {
                        "link": "https://www.sharecancersupport.org/2008/08/how-i-survived-triple-negative-breast-cancer/",
                        "title": "Chiara: How I Survived Triple Negative Breast Cancer",
                        "description": "After a mammogram, ultrasound, MRI, chest and abdomen CT scan, bone scan and a few biopsies, I received the diagnosis of triple negative breast cancer."
                    },
                    {
                        "link": "http://www.annpietrangelo.com/cancer_series.php",
                        "title": "Living with Triple Negative Breast Cancer Series .:. Ann Pietrangelo .:. A Writer’s Journey",
                        "description": "Links to blog posts Living with Triple Negative Breast Cancer by Ann Pietrangelo"
                    },
                    {
                        "link": "https://www.youngsurvival.org/blog/survivor-stories/survivor/jennifer",
                        "title": "Jennifer | Young Survival Coalition, Young women facing breast cancer together.",
                        "description": "I don't want to identify myself with anything cancer. Yes, it happened to me but no, it is not a part of who I am. Like any other negative experience in your life, you get through it, you learn from it, and you move on."
                    },
                    {
                        "link": "https://forum.breastcancercare.org.uk/t5/Triple-negative/Any-triple-negative-survivors-out-there/td-p/685856",
                        "title": " Any triple negative survivors out there? - Breast Cancer Care Forum - 685856",
                        "description": "Hi I was diagnosed with triple negative invasive breast cancer with positive lymph nodes on 21st may. Had my 4th blast of chemo on Thursday, - 685856"
                    },
                    {
                        "link": "https://netflixandchemo.com/",
                        "title": "netflixandchemo – triple negative breast cancer. mostly positive blogger",
                        "description": "triple negative breast cancer. mostly positive blogger"
                    },
                    {
                        "link": "http://katydidcancer.blogspot.com/2014/03/day-1358-triple-negative-breast-cancer.html",
                        "title": "KatyDid Cancer: Day 1,358: Triple Negative Breast Cancer Awareness Day",
                        "description": "The looks you receive are almost too much to bear. The gynecologists who look shocked and afraid for you. The friends who don\'t understand w"
                    },
                    {
                        "link": "http://www.joanlunden.com/category/35-breast-cancer/item/579-what-is-triple-negative-breast-cancer",
                        "title": "What is Triple Negative Breast Cancer? | Joan Lunden",
                        "description": "Creating a healthy lifestyle for a better tomorrow"
                    },
                    {
                        "link": "https://www.triplenegative.co.uk/blog/",
                        "title": "Blogs. Triple Negative Breast Cancer",
                        "description": "Blogs. Triple Negative Breast Cancer"
                    }
                ],
                "pubmed": [
                    {
                        "link": "https://www.ncbi.nlm.nih.gov/pubmed/21278435",
                        "title": "Triple-negative breast cancer: an unmet medical need.  - PubMed - NCBI",
                        "description": "Oncologist. 2011;16 Suppl 1:1-11. doi: 10.1634/theoncologist.2011-S1-01. Research Support, Non-U.S. Gov't; Review"
                    },
                    {
                        "link": "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4881925/",
                        "title": "Triple-negative breast cancer: treatment challenges and solutions",
                        "description": "Triple-negative breast cancers (TNBCs) are defined by the absence of estrogen and progesterone receptors and the absence of HER2 overexpression. These cancers represent a heterogeneous breast cancer subtype with a poor prognosis. Few systemic treatment"
                    },
                    {
                        "link": "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4181680/",
                        "title": "Triple Negative Breast Cancer – An Overview",
                        "description": "Triple Negative Breast Cancer (TNBC) is a heterogeneous disease that based on immunohistochemistry (IHC) is estrogen receptor (ER) negative, progesterone receptor (PR) negative and human epidermal growth factor receptor 2 (HER2) negative. TNBC is typically"
                    },
                    {
                        "link": "https://www.ncbi.nlm.nih.gov/pubmed/27249684",
                        "title": "The Evolution of Triple-Negative Breast Cancer: From Biology to Novel Therapeutics.  - PubMed - NCBI",
                        "description": "Am Soc Clin Oncol Educ Book. 2016;35:34-42. doi: 10.14694/EDBK_159135. Review"
                    },
                    {
                        "link": "https://www.ncbi.nlm.nih.gov/pubmed/25285241",
                        "title": "Triple Negative Breast Cancer - An Overview.  - PubMed - NCBI",
                        "description": "Hereditary Genet. 2013;2013(Suppl 2). pii: 001."
                    },
                    {
                        "link": "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC2868264/",
                        "title": "Understanding and Treating Triple-Negative Breast Cancer",
                        "description": "Triple-negative breast cancer is a subtype of breast cancer that is clinically negative for expression of estrogen and progesterone receptors (ER/PR) and HER2 protein. It is characterized by its unique molecular profile, aggressive behavior, distinct"
                    },
                    {
                        "link": "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5008562/",
                        "title": "Features of triple-negative breast cancer",
                        "description": "The aim of this study was to determine the features of triple-negative breast cancer (TNBC) using a large national database. TNBC is known to be an aggressive subtype, but national epidemiologic data are sparse. All patients with invasive breast cancer"
                    },
                    {
                        "link": "https://www.ncbi.nlm.nih.gov/pubmed/21067385",
                        "title": "Triple-negative breast cancer.  - PubMed - NCBI",
                        "description": "N Engl J Med. 2010 Nov 11;363(20):1938-48. doi: 10.1056/NEJMra1001389. Research Support, Non-U.S. Gov't; Review"
                    },
                    {
                        "link": "https://www.ncbi.nlm.nih.gov/pubmed/27221827",
                        "title": "Recent Progress in Triple Negative Breast Cancer Research.  - PubMed - NCBI",
                        "description": "Asian Pac J Cancer Prev. 2016;17(4):1595-608. Review"
                    },
                    {
                        "link": "https://www.ncbi.nlm.nih.gov/pubmed/24619745",
                        "title": "Triple-negative breast carcinoma: current and emerging concepts.  - PubMed - NCBI",
                        "description": "Am J Clin Pathol. 2014 Apr;141(4):462-77. doi: 10.1309/AJCPQN8GZ8SILKGN. Review"
                    }
                ],
                "news_articles": [
                    {
                        "link": "https://www.medicalnewstoday.com/articles/320871.php",
                        "title": "This protein fuels triple-negative breast cancer",
                        "description": "Researchers report that they have identified a new stem cell pathway that drives the development of highly aggressive triple-negative breast cancer."
                    },
                    {
                        "link": "https://medicalxpress.com/news/2018-02-uncovers-therapeutic-aggressive-triple-negative-breast.html",
                        "title": "Study uncovers therapeutic targets for aggressive triple-negative breast cancers",
                        "description": "As part of a breast-cancer diagnosis, doctors analyze the tumor to determine which therapies might best attack the malignancy. But for patients whose cancer is triple-negative—that is, lacking receptors for estrogen, progesterone"
                    },
                    {
                        "link": "https://www.dovepress.com/neoadjuvant-treatments-in-triple-negative-breast-cancer-patients-where-peer-reviewed-article-CMAR",
                        "title": "Neoadjuvant treatments in triple-negative breast cancer patients: wher | CMAR",
                        "description": "Neoadjuvant treatments in triple-negative breast cancer patients: where we are now and where we are going Claudia Omarini, Giorgia Guaitoli, Stefania Pipitone, Luca Moscetti, Laura Cortesi, Stefano Cascinu, Federico Piacentini Department of Medical and Surgical Sciences for"
                    },
                    {
                        "link": "http://www.precisionvaccinations.com/cancer-vaccine-candidate-tpiv200-treating-triple-negative-breast-cancer-launches-phase-2-clinical",
                        "title": "Breast Cancer Vaccine Candidate Launches Phase 2 Clinical Study — Precision Vaccinations",
                        "description": "A leading clinical-stage immuno-oncology company has enrolled the final patient need to launch a randomized Phase 2 clinical study of a T-cell vaccine candidate TPIV200 for treating triple-negative breast cancer (TNBC)"
                    },
                    {
                        "link": "http://www.onclive.com/onclive-tv/dr-bardia-on-sacituzumab-govitecan-in-triplenegative-breast-cancer",
                        "title": "Dr. Bardia on Sacituzumab Govitecan in Triple-Negative Breast Cancer",
                        "description": "Aditya Bardia, MD, MPH, assistant professor of medicine, Harvard Medical School, attending physician, Medical Oncology, Massachusetts General Hospital, discusses a trial investigating sacituzumab govitecan for patients with triple-negative breast cancer (TNBC)."
                    },
                    {
                        "link": "https://www.newsday.com/news/health/breast-cancer-genetic-1.16262137",
                        "title": "Doctors explore causes of breast cancer | Newsday",
                        "description": "For some, genetics explain a cancer that looms large on Long Island’s health care landscape. For others, the cause of breast cancer is a mystery."
                    },
                    {
                        "link": "https://www.news-medical.net/?tag=/Triple-Negative-Breast-Cancer",
                        "title": "Triple Negative Breast Cancer News, Research",
                        "description": "Triple Negative Breast Cancer News, Research"
                    },
                    {
                        "link": "https://www.curetoday.com/articles/big-change-is-coming-for-the-treatment-of-triple-negative-breast-cancer",
                        "title": "Big Change Is Coming for the Treatment of Triple-Negative Breast Cancer",
                        "description": "The treatment landscape of triple-negative breast cancer is vastly changing. CURE spoke with&nbsp;Joyce A. O&rsquo;Shaughnessy, M.D. about what to expect."
                    },
                    {
                        "link": "https://www.prnewswire.com/news-releases/oncosec-provides-encouraging-clinical-observations-related-to-triple-negative-breast-cancer-study-300584586.html",
                        "title": " OncoSec Provides Encouraging Clinical Observations Related To Triple Negative Breast Cancer Study",
                        "description": "SAN DIEGO, Jan. 18, 2018 /PRNewswire/ -- OncoSec Provides Encouraging Clinical Observations Related To Triple Negative Breast Cancer Study."
                    },
                    {
                        "link": "http://www.ascopost.com/issues/august-10-2017/advances-in-the-treatment-of-triple-negative-breast-cancer/",
                        "title": "Advances in the Treatment of Triple-Negative Breast Cancer - The ASCO Post",
                        "description": "Advances in the Treatment of Triple-Negative Breast Cancer - The ASCO Post"
                    }
                ]
            }
        elif dd.get('ethnicity') == 'Asian':
            data = {
                "google_links": [
                    {
                        "link": "http://ww5.komen.org/BreastCancer/RaceampEthnicity.html",
                        "title": "Race, Ethnicity, and Breast Cancer | Susan G. Komen®",
                        "description": "Learn how rates of breast cancer in the U.S. vary by race and ethnicity."
                    },
                    {
                        "link": "https://www.curetoday.com/articles/breast-cancer-incidences-increasing-in-asianamerican-women",
                        "title": "Breast Cancer Incidences Increasing in Asian-American Women",
                        "description": "Despite the incidence of breast cancer either holding steady or decreasing in other U.S. racial/ethnic groups, it has been increasing in Asian-American women for the past 25 years."
                    },
                    {
                        "link": "https://dceg.cancer.gov/research/cancer-types/breast-cancer/breast-asian-women",
                        "title": "Breast Cancer Among Asian Women - National Cancer Institute",
                        "description": "Study of breast cancer study among Asian women, to identify molecular alterations in tumors and examine associations of molecular changes with risk factors."
                    },
                    {
                        "link": "https://www.nbcnews.com/news/asian-america/breast-cancer-rates-rise-among-asian-american-women-others-stay-n749366",
                        "title": "Breast Cancer Rates Rise Among Asian-American Women as Others Stay Stable",
                        "description": "Breast cancer rates have been increasing among Asian-American women over the past 15 years, according to the Cancer Prevention Institute of California"
                    },
                    {
                        "link": "https://www.huffingtonpost.com/entry/asian-american-women-breast-cancer_us_596d181be4b0e983c0584166",
                        "title": "More Asian-Americans Are Facing Breast Cancer And Westernization May Be Why | HuffPost",
                        "description": "Women could be suffering the unintended consequences of assimilation"
                    },
                    {
                        "link": "https://www.maurerfoundation.org/breast-cancer-rates-increasing-among-asian-americans/",
                        "title": "Breast Cancer Rates Increasing Among Asian Americans",
                        "description": "Researchers examined breast cancer incidence rates among seven Asian American ethnic groups in this new study. FREMONT, CA (April 10, 2017) — In contrast"
                    },
                    {
                        "link": "http://cancerpreventionresearch.aacrjournals.org/content/early/2017/12/08/1940-6207.CAPR-17-0283",
                        "title": "Adiposity, Inflammation and Breast Cancer Pathogenesis in Asian Women | Cancer Prevention Research",
                        "description": "Obesity is associated with white adipose tissue (WAT) inflammation in the breast, elevated levels of the estrogen biosynthetic enzyme, aromatase, and systemic changes that predispose to breast cancer development"
                    },
                    {
                        "link": "http://www.breastcancer.org/research-news/20070928",
                        "title": "More Asian Women Being Diagnosed With Breast Cancer",
                        "description": "More Asian Women Being Diagnosed With Breast Cancer"
                    },
                    {
                        "link": "https://www.cdc.gov/cancer/breast/statistics/race.htm",
                        "title": "CDC - Breast Cancer Rates by Race and Ethnicity",
                        "description": "Breast cancer statistics from CDC: incidence and mortality by race and ethnicity."
                    },
                    {
                        "link": "https://www.sciencedirect.com/science/article/pii/S0960076009003100",
                        "title": "Unique features of breast cancer in Asian women—Breast cancer in Taiwan as an example - ScienceDirect",
                        "description": "Unique features of breast cancer in Asian women—Breast cancer in Taiwan as an example - ScienceDirect"
                    }
                ],
                "blogs_and_posts": [
                    {
                        "link": "http://www.lbbc.org/node/5882",
                        "title": "Finding New Purpose: Chien-Chi Huang | Living Beyond Breast Cancer",
                        "description": " The scariest part of my cancer journey was not losing my hair or my breast. It was losing my mind.”That’s how Chien-Chi Huang recalls the year she was treated for triple-negative breast cancer."
                    },
                    {
                        "link": "https://themighty.com/2018/01/cultural-chasm-challenges-asian-american-breast-cancer-survivor/",
                        "title": "The Challenges of Being a Young Asian American Breast Cancer Survivor | The Mighty",
                        "description": "A young Asian American woman who survived breast cancer shares the cultural differences and challenges of being a cancer survivor."
                    },
                    {
                        "link": "http://www.thermographyclinic.com/blog/entry/the-secret-of-asian-women",
                        "title": "The Secret of Asian Women - Thermography Clinic Blog",
                        "description": "It is a well-known fact that Asian women have a much lower incidence of breast cancer compared to women in North America and Western Europe. Women in Japan for instance have one seventh of breast cancer rates compared to women in US and Canada."
                    },
                    {
                        "link": "http://www.plumblossoms.me/introduction.html",
                        "title": "Introduction  - plumblossoms",
                        "description": "That question kept popping up after I was diagnosed in 2009 with Stage 1 breast cancer. Through personal referrals, scores of Caucasian women—complete strangers—graciously spoke on the phone"
                    },
                    {
                        "link": "http://www.ocbreastwellness.com/question-soy-effect-breast-cancer/",
                        "title": "The Question of Soy and its Effect on Breast Cancer",
                        "description": "The question of soy and its effect on breast cancer."
                    },
                    {
                        "link": "http://blog.marykayfoundation.org/corporate/archive/2017/05/17/cancer-news-and-how-it-affects-you.aspx",
                        "title": "The Mary Kay Foundation Blog | Inspiring Beauty Through Caring",
                        "description": "The Official Mary Kay Foundation Blog – Our mission is to eliminate cancers affecting women and to end the epidemic of violence against women."
                    },
                    {
                        "link": "https://community.breastcancer.org/forum/83/topics/862382?page=1#post_5146038",
                        "title": "Breast Cancer Topic: Worried about symptoms",
                        "description": "Breast Cancer Discussion Forums - Access the shared knowledge of thousands of people affected by breast cancer"
                    },
                    {
                        "link": "http://yourhealthblog.net/more-young-asian-women-are-diagnosed-with-breast-cancer/",
                        "title": "More young Asian women are diagnosed with breast cancer – Health Blog Centre Info",
                        "description": "More young Asian women are diagnosed with breast cancer – Health Blog Centre Info"
                    },
                    {
                        "link": "http://blog.angryasianman.com/2016/10/why-asian-breast-cancer.html",
                        "title": " Why Asian Breast Cancer?",
                        "description": "Guest Post by Stephen Christopher Liu"
                    },
                    {
                        "link": "https://www.sbi-online.org/endtheconfusion/Blog/TabId/546/ArtMID/1586/ArticleID/407/Racial-Disparities-in-Breast-Cancer-Screening.aspx",
                        "title": "Racial Disparities in Breast Cancer Screening",
                        "description": "I get this weird phone call every July from my mom. “Do I really have to?” “Yes, mom, you do. Each and every single year.” My mom absolutely abhors mammograms, and she calls me every summer asking me if she really needs her annual mammogram"
                    }
                ],
                "pubmed": [
                    {
                        "link": "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC2837454/",
                        "title": "Hidden Breast Cancer Disparities in Asian Women: Disaggregating Incidence Rates by Ethnicity and Migrant Status",
                        "description": "Objectives. We estimated trends in breast cancer incidence rates for specific Asian populations in California to determine if disparities exist by immigrant status and age.Methods. To calculate rates by ethnicity and immigrant status, we obtained data"
                    },
                    {
                        "link": "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC2853623/",
                        "title": "Disparities in Breast Cancer Survival Among Asian Women by Ethnicity and Immigrant Status: A Population-Based Study",
                        "description": "Objectives. We investigated heterogeneity in ethnic composition and immigrant status among US Asians as an explanation for disparities in breast cancer survival.Methods. We enhanced data from the California Cancer Registry and the Surveillance, Epidemiology, "
                    },
                    {
                        "link": "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5160133/",
                        "title": "Breast Density and Risk of Breast Cancer in Asian Women: A Meta-analysis of Observational Studies",
                        "description": "The established theory that breast density is an independent predictor of breast cancer risk is based on studies targeting white women in the West. More Asian women than Western women have dense breasts, but the incidence of breast cancer is lower among"
                    },
                    {
                        "link": "https://www.ncbi.nlm.nih.gov/pubmed/20147696",
                        "title": "Hidden breast cancer disparities in Asian women: disaggregating incidence rates by ethnicity and migrant status.  - PubMed - NCBI",
                        "description": "Am J Public Health. 2010 Apr 1;100 Suppl 1:S125-31. doi: 10.2105/AJPH.2009.163931. Epub  2010 Feb 10. Research Support, N.I.H., Extramural; Research Support, Non-U.S. Gov't; Research Support, U.S. Gov't, P.H.S."
                    },
                    {
                        "link": "https://www.ncbi.nlm.nih.gov/pubmed/22638769",
                        "title": "Breast cancer risk factors differ between Asian and white women with BRCA1/2 mutations.  - PubMed - NCBI",
                        "description": "Fam Cancer. 2012 Sep;11(3):429-39. doi: 10.1007/s10689-012-9531-9. Research Support, N.I.H., Extramural"
                    },
                    {
                        "link": "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4929251/",
                        "title": "Breast Cancer Mortality among Asian-American Women in California: Variation according to Ethnicity and Tumor Subtype",
                        "description": "Asian-American women have equal or better breast cancer survival rates than non-Hispanic white women, but many studies use the aggregate term Asian/Pacific Islander (API) or consider breast cancer as a single disease. The purpose of this study was to "
                    },
                    {
                        "link": "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4069805/",
                        "title": "Incidence and mortality of female breast cancer in the Asia-Pacific region",
                        "description": "To provide an overview of the incidence and mortality of female breast cancer for countries in the Asia-Pacific region.Statistical information about breast cancer was obtained from publicly available cancer registry and mortality databases (such as GLOBOCAN), "
                    },
                    {
                        "link": "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4607827/",
                        "title": "Female breast cancer in Vietnam: a comparison across Asian specific regions",
                        "description": "Breast cancer is one of the most commonly diagnosed malignancies and the leading cause of cancer death of women over the world. A large number of females with breast cancer in Vietnam and other Southeast Asian (SEA) countries present at an early age with "
                    },
                    {
                        "link": "https://www.ncbi.nlm.nih.gov/pubmed/17387549",
                        "title": "Spectrum of breast cancer in Asian women.  - PubMed - NCBI",
                        "description": "World J Surg. 2007 May;31(5):1031-40. Comparative Study; Multicenter Study"
                    },
                    {
                        "link": "https://www.ncbi.nlm.nih.gov/pubmed/25374197",
                        "title": "Attitudes of South Asian women to breast health and breast cancer screening: findings from a community based sample in the United States.  - PubMed - NCBI",
                        "description": "Asian Pac J Cancer Prev. 2014;15(20):8719-24."
                    }
                ],
                "news_articles": [
                    {
                        "link": "http://www.abc.net.au/news/health/2018-02-03/how-cultural-barriers-can-hamper-breast-cancer-screening/9391388",
                        "title": "Breast cancer screening and cultural barriers: Why some women are missing early detection - Health - ABC News",
                        "description": "When it comes to breast cancer screening, there are complex cultural barriers that can hamper important messages about early detection. New research suggests many migrant Australian women are still not breast aware."
                    },
                    {
                        "link": "http://sampan.org/2018/02/duke-university-seeking-chinese-japanese-and-korean-breast-cancer-survivors-for-study/",
                        "title": "Duke University seeking Chinese, Japanese and Korean breast cancer survivors for study – Sampan.org",
                        "description": "In Asian American women, breast cancer is the leading cancer by site. Furthermore, for some sub-ethnic groups, breast cancer is the leading cause of death. Breast cancer is certainly a significant health concern among Asian American women"
                    },
                    {
                        "link": "http://gulftoday.ae/portal/79f8e21e-70bc-4175-9fbf-ffb8a0374eb8.aspx",
                        "title": "gulftoday.ae | Pink Caravan Ride – the untold stories",
                        "description": "gulftoday.ae | Pink Caravan Ride – the untold stories"
                    },
                    {
                        "link": "http://www.asianage.com/life/health/080218/breast-cancer-survivors-may-die-of-heart-disease-doctors-warn.html",
                        "title": "Breast cancer survivors may die of heart disease, doctors warn",
                        "description": "Chemotherapy can weaken heart muscle, some newer medicines can increase risk of heart failure, radiation can cause heart rhythm disorders"
                    },
                    {
                        "link": "https://www.medicalnewstoday.com/articles/320683.php",
                        "title": "Hormone-fueled breast cancer cells halted with new approach",
                        "description": "Scientists identify where hormone-fueled breast cancer cells derive their energy from, and they find a way to block their access to it. "
                    },
                    {
                        "link": "https://www.bustle.com/p/what-the-age-you-got-your-first-period-at-says-about-your-health-according-to-science-8064600",
                        "title": "What The Age You Got Your First Period At Says About Your Health, According To Science",
                        "description": "When is the normal time to begin your period? If you're around 13 at the age of your first menarche, which is the technical Greek term for your first menstruation, you're in the most common range. That's a lot younger than many of your ancestors; sâ\u0080¦"
                    },
                    {
                        "link": "http://www.businesstimes.com.sg/brunch/out-of-the-loop",
                        "title": "Out of the loop, Brunch - THE BUSINESS TIMES",
                        "description": ": THE BUSINESS TIMES Brunch - Bayer eventually pulled sales of Essure from markets outside the United States last September, citing commercial reasons.. Read more at The Business Times."
                    },
                    {
                        "link": "https://www.curetoday.com/articles/breast-cancer-incidences-increasing-in-asianamerican-women",
                        "title": "Breast Cancer Incidences Increasing in Asian-American Women",
                        "description": "Despite the incidence of breast cancer either holding steady or decreasing in other U.S. racial/ethnic groups, it has been increasing in Asian-American women for the past 25 years."
                    },
                    {
                        "link": "http://managedhealthcareexecutive.modernmedicine.com/managed-healthcare-executive/news/asian-american-women-need-better-targeted-breast-cancer-therapy",
                        "title": "Asian-American women need better targeted breast cancer therapy | Managed Healthcare Executive",
                        "description": "Breast cancer incidence rates have risen steadily in the past 15 years among California Asian Americans in contrast to other U.S. racial/ethnic groups, with the greatest increases in Koreans, South"
                    },
                    {
                        "link": "http://www.scmp.com/lifestyle/health-beauty/article/2116762/two-big-myths-about-breast-cancer-and-what-hong-kong-women",
                        "title": "Two big myths about breast cancer – and what Hong Kong women really need to know | South China Morning Post",
                        "description": "Misconceptions still surround the disease, that prevent the city’s women taking the illness seriously and getting screened regularly for it"
                    }
                ]
            }
        elif dd.get('ethnicity') == 'African American':
            data = {
                "google_links": [
                    {
                        "link": "http://www.sistersnetworkinc.org/breastcancerfacts.html",
                        "title": "Sisters Network Inc. : A National African American Breast Cancer Survivorship Organization",
                        "description": "Sisters Network Inc. : A National African American Breast Cancer Survivorship Organization"
                    },
                    {
                        "link": "http://theoncologist.alphamedpress.org/content/10/1/1.full",
                        "title": "Breast Cancer in African-American Women ",
                        "description": "The Oncologist is a journal devoted to medical and practice issues for surgical, radiation, and medical oncologists."
                    },
                    {
                        "link": "https://www.bwhi.org/2017/07/20/black-women-breast-cancer-diagnosis-care/",
                        "title": "Black Women And Breast Cancer: Why Our Diagnosis And Care Are Different",
                        "description": "Here are some questions and answers about Black women and breast cancer from the Breast Cancer Research Foundation’s Marc Hurlbert, PhD."
                    },
                    {
                        "link": "https://www.cancer.org/latest-news/report-breast-cancer-rates-rising-among-african-american-women.html",
                        "title": "Report: Breast Cancer Rates Rising Among African-American Women",
                        "description": "A new report from the American Cancer Society finds that breast cancer rates among African-American women in the United States are increasing."
                    },
                    {
                        "link": "https://www.cdc.gov/healthcommunication/toolstemplates/entertainmented/tips/BreastCancerAfricanAmerican.html",
                        "title": "Breast Cancer in Young African American Women | Gateway to Health Communication | CDC",
                        "description": "Breast Cancer - Gateway to Health Communication - CDC"
                    },
                    {
                        "link": "https://aabcainc.org/facts-to-know/",
                        "title": "African American Breast Cancer Alliance  » Facts to Know",
                        "description": "African American Breast Cancer Alliance  » Facts to Know"
                    },
                    {
                        "link": "https://www.bcrf.org/blog/why-black-women-are-more-likely-die-breast-cancer",
                        "title": "Why Black Women Are More Likely to Die of Breast Cancer | BCRF",
                        "description": "Over the last 20 years, there has been a major problem in breast cancer prevention, diagnosis, and care: While overall mortality rates have improved by more than 30%, the bad news is that black women are still more likely to die from the disease than white women—and the disparity"
                    },
                    {
                        "link": "https://blackdoctor.org/515014/breaking-black-woman-developed-alternative-to-breast-cancer-treatment/",
                        "title": "Black Woman Developed Alternative To Breast Cancer Treatment",
                        "description": "Triple negative breast cancer, which has been plaguing women, black women in particular, for years, is getting a new treatment thanks to"
                    },
                    {
                        "link": "https://www.webmd.com/breast-cancer/news/20161003/breast-cancer-deaths-black-women",
                        "title": "Breast Cancer Deaths Increasing for Black Women",
                        "description": "Atlanta tops list of 10 deadliest cities for African-American women dying from breast cancer, but Austin, Dallas, Memphis, Los Angeles, Chicago, and others are not far behind. "
                    },
                    {
                        "link": "https://www.cancer.gov/about-nci/organization/crchd/cancer-health-disparities-fact-sheet",
                        "title": "Cancer Health Disparities - National Cancer Institute",
                        "description": "A fact sheet that describes the incidence and death rates for selected cancers among racial and ethnic groups living in the United States."
                    }
                ],
                "blogs_and_posts": [
                    {
                        "link": "http://www.lbbc.org/african-american",
                        "title": "African-American | Living Beyond Breast Cancer",
                        "description": "Content coming soon!"
                    },
                    {
                        "link": "https://community.breastcancer.org/forum/98",
                        "title": "Breast Cancer Forum: African Americans With Breast Cancer",
                        "description": "Breast Cancer Discussion Forums - Access the shared knowledge of thousands of people affected by breast cancer"
                    },
                    {
                        "link": "http://nautil.us/blog/why-are-black-women-more-likely-to-die-from-breast-cancer",
                        "title": "Genetic cancer screening is a microcosm of racial disparities in breast cancer care",
                        "description": "Here’s a curious fact: Black American women are 37 percent more likely to die from breast cancer than white women, according to"
                    },
                    {
                        "link": "https://www.onemedical.com/blog/live-well/black-women-breast-cancer/",
                        "title": "Rising Rates of Breast Cancer in African American Women | One Medical",
                        "description": "Our experienced San Francisco Bay Area doctors apply a modern approach and a caring touch to provide you with the highest quality health care. Find out how."
                    },
                    {
                        "link": "https://publichealthmatters.blog.gov.uk/2016/12/08/improving-understanding-of-breast-cancer-survival-in-black-women/",
                        "title": "Improving understanding of breast cancer survival in black women - Public health matters",
                        "description": "The official blog of Public Health England, providing insight and commentary on all aspects of public health, including health protection, health improvement, wellbeing, data and knowledge"
                    },
                    {
                        "link": "http://blog.thebreastcancersite.com/exercise-reduces-breast-cancer-risk-in-african-american-women/",
                        "title": "Exercise Reduces Breast Cancer Risk in African-American Women |  The Breast Cancer Site Blog",
                        "description": "A new study by researchers at Boston University School of Public Health found that African-American women who partake in regular exercise may be able to reduce their risk of breast cancer"
                    },
                    {
                        "link": "http://www.criteriuminc.com/wordpress/index.php/2017/10/",
                        "title": "October | 2017 | Get To Know Your CRO - The Criterium Blog",
                        "description": "October | 2017 | Get To Know Your CRO - The Criterium Blog"
                    },
                    {
                        "link": "https://www.cityofhope.org/blog/black-women-breast-cancer",
                        "title": "Black women need special support during, and after, breast cancer",
                        "description": "City of Hope program helps black breast cancer survivors improve their overall health by navigating them through their treatment and follow-up care."
                    }
                ],
                "pubmed": [
                    {
                        "link": "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3955723/",
                        "title": "African American Women’s Perspectives on Breast Cancer: Implications for Communicating Risk of Basal-like Breast Cancer",
                        "description": "African American women suffer a higher burden of basal-like breast cancer, an aggressive subtype that has no targeted therapy. While epidemiologic research has identified key prevention strategies, little is known about how best to communicate risk to"
                    },
                    {
                        "link": "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC1447112/",
                        "title": "Impact of Breast Cancer on African American Women: Priority Areas for Research in the Next Decade",
                        "description": "Despite all the gains that have been made in the area of breast cancer research, African American women suffer disproportionately from the effects of the disease. Breast cancer is the second leading cause of cancer death among African American women, "
                    },
                    {
                        "link": "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC2568204/",
                        "title": "Breast cancer risk factors in African-American women: the Howard University Tumor Registry experience.",
                        "description": "This retrospective case-control study examines risk factors for breast cancer in African-American women, who recently have shown an increase in the incidence of this malignancy, especially in younger women. Our study involves 503 cases from the Howard"
                    },
                    {
                        "link": "https://www.ncbi.nlm.nih.gov/pubmed/16951137",
                        "title": "Breast cancer in African-American women: differences in tumor biology from European-American women.  - PubMed - NCBI",
                        "description": "Cancer Res. 2006 Sep 1;66(17):8327-30. Comparative Study; Research Support, N.I.H., Extramural; Research Support, U.S. Gov't, Non-P.H.S.; Review"
                    },
                    {
                        "link": "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4730397/",
                        "title": "African American Women: Surviving Breast Cancer Mortality against the Highest Odds",
                        "description": "Among the country’s 25 largest cities, the breast cancer mortality disparity is highest in Memphis, Tennessee, where African American women are twice as likely to die from breast cancer as White women. This qualitative study of African-American ..."
                    },
                    {
                        "link": "https://www.ncbi.nlm.nih.gov/pubmed/27995352",
                        "title": "Diabetes and breast cancer mortality in Black women.  - PubMed - NCBI",
                        "description": "Cancer Causes Control. 2017 Jan;28(1):61-67. doi: 10.1007/s10552-016-0837-z. Epub  2016 Dec 19."
                    },
                    {
                        "link": "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3603001/",
                        "title": "Breast cancer epidemiology in blacks and whites: disparities in incidence, mortality, survival rates and histology",
                        "description": "This study presents black-white breast cancer statistics, tumor histology and receptor status, and treatment patterns for all ages and by age groups (under 40, between ages 40 and 49, and age 50 and over).The study used data from the National Cancer Institute"
                    },
                    {
                        "link": "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4879045/",
                        "title": "Medical Advocacy Among African American Women Diagnosed with Breast Cancer: From Recipient to Resource",
                        "description": "Medical advocacy at multiple levels (self, community/interpersonal, national/public health interest) may be helpful to address the disproportionate burden of breast cancer African American women encounter. Little however is known about the interplay of"
                    },
                    {
                        "link": "https://www.ncbi.nlm.nih.gov/pubmed/23539135",
                        "title": "Black women's awareness of breast cancer disparity and perceptions of the causes of disparity.  - PubMed - NCBI",
                        "description": "J Community Health. 2013 Aug;38(4):766-72. doi: 10.1007/s10900-013-9677-x. Research Support, Non-U.S. Gov't"
                    },
                    {
                        "link": "https://www.ncbi.nlm.nih.gov/pubmed/25673085",
                        "title": "Triple-negative breast cancer in African-American women: disparities versus biology.  - PubMed - NCBI",
                        "description": "Nat Rev Cancer. 2015 Apr;15(4):248-54. doi: 10.1038/nrc3896. Epub  2015 Feb 12. Research Support, N.I.H., Extramural; Research Support, Non-U.S. Gov't; Review"
                    }
                ],
                "news_articles": [
                    {
                        "link": "http://www.nydailynews.com/life-style/breast-cancer-kills-black-women-higher-rate-white-women-article-1.3553618",
                        "title": "Breast cancer kills black women at a higher rate than white women - NY Daily News",
                        "description": "The American Cancer Society said in a new report that white women have a 39% greater chance of surviving breast cancer than black women."
                    },
                    {
                        "link": "https://www.hsph.harvard.edu/news/features/jim-crow-breast-cancer-black-women/",
                        "title": "Jim Crow laws: A contributing factor to more lethal breast cancer among U.S. black women now? | News | Harvard T.H. Chan School of Public Health",
                        "description": "November 1, 2017 – Jim Crow laws—which legalized racial discrimination in Southern U.S. states from the late 1870s through the mid-1960s—have been linked with negative health impacts. A new study "
                    },
                    {
                        "link": "http://www.13wmaz.com/news/local/alarming-statistic-shows-african-american-women-more-likely-to-die-from-breast-cancer/512621965",
                        "title": "Alarming statistic shows African American women are more likely to die from breast cancer | 13wmaz.com",
                        "description": "According to the American Cancer Society, white women are more likely to be diagnosed with breast cancer, but African American women are more likely to die from it"
                    },
                    {
                        "link": "http://www.radiologybusiness.com/topics/care-delivery/obstacle-or-death-sentence-how-women%E2%80%99s-experiences-shape-their-views-breast-cancer",
                        "title": "Obstacle or death sentence? How women’s experiences shape views of breast cancer | Radiology Business",
                        "description": "A woman’s memories of breast cancer—whether they stem from a family member’s diagnosis or a close friend’s battle—could significantly shape that woman’s choices about her own preventive care, researchers reported in the Journal of Health Psychology."
                    },
                    {
                        "link": "https://www.oncologynurseadvisor.com/breast-cancer/cardiotoxicity-risk-greater-in-blacks-with-breast-cancer-receiving-her2-therapies/article/741433/",
                        "title": "Cardiotoxicity Risk Greater in Blacks With Breast Cancer Receiving HER2 Therapies - ONA",
                        "description": "Black patients with breast cancer treated with HER2-targeted therapies are more prone to cardiotoxicity leading to incomplete adjuvant therapy compared with white patients, research data indicates."
                    },
                    {
                        "link": "https://www.alcoholproblemsandsolutions.org/risk-of-breast-cancer-in-african-american-women/",
                        "title": "Breast Cancer in African-American Women: Is Alcohol a Risk Factor for Black Women?",
                        "description": "Risk of breast cancer in African-American women not increased by drinking alcohol either recently or for a lifetime in this case-control US study."
                    },
                    {
                        "link": "https://www.reuters.com/article/us-health-breastcancer-insurance-mortali/insurance-a-major-factor-in-blacks-higher-breast-cancer-mortality-idUSKBN1CO21Q",
                        "title": "Insurance a major factor in blacks’ higher breast cancer mortality | Reuters",
                        "description": "By Anne Harding(Reuters Health) - African-American women have worse breast cancer survival than white women in the U.S., and a new study suggests that is largely because black women are less likely to have health insurance."
                    },
                    {
                        "link": "https://www.blackwomenshealth.org/issues-and-resources/black-women-and-breast-cancer.html",
                        "title": "Black Women's Health Imperative - Black Women and Breast Cancer",
                        "description": "Black Women's Health Imperative - Black Women and Breast Cancer"
                    },
                    {
                        "link": "https://health.usnews.com/health-care/articles/2017-11-15/diabetes-may-be-driving-high-rates-of-breast-cancer-in-black-women",
                        "title": "Diabetes May Be Driving High Rates of Breast Cancer in Black Women | Health Care | US News",
                        "description": "US News is a recognized leader in college, grad school, hospital, mutual fund, and car rankings.  Track elected officials, research health conditions, and find news you can use in politics, business, health, and education."
                    },
                    {
                        "link": "https://uknowledge.uky.edu/comm_etds/63/",
                        "title": "BLACK WOMEN’S PERSPECTIVES ON BREAST CANCER DETECTION MESSAGING by Denise M. Damron",
                        "description": "A qualitative approach was used to explore the influence of mass media campaigns on Black women’s perceptions of breast cancer."
                    }
                ]
            }
        elif dd.get('age') < 40:
            data = {
                "google_links": [
                    {
                        "link": "https://ww5.komen.org/BreastCancer/YoungWomenandBreastCancer.html",
                        "title": "Unique Issues for Young Women with Breast Cancer | Susan G. Komen®",
                        "description": "Learn about the unique issues young women with breast cancer face including early menopause, fertility concerns and more. Find out about clinical trials and support."
                    },
                    {
                        "link": "https://www.webmd.com/breast-cancer/breast-cancer-young-women",
                        "title": "Breast Cancer in Young Women",
                        "description": "Learn more from WebMD about breast cancer in younger women, including risk factors, screening schedules, and treatment options."
                    },
                    {
                        "link": "http://www.lbbc.org/young-woman-breast-cancer",
                        "title": "Young Women with Breast Cancer | Living Beyond Breast Cancer",
                        "description": "As a young woman with breast cancer, you may have concerns about choosing treatment, coping with your diagnosis & planning for your future. Learn more here."
                    },
                    {
                        "link": "https://www.healthline.com/health/breast-cancer/breast-cancer-in-young-women",
                        "title": "Breast Cancer In Young Women: How Is It Different?",
                        "description": "Receiving a breast cancer diagnosis can be challenging, no matter your age. Young women often face a unique set of concerns. Learn more."
                    },
                    {
                        "link": "https://www.breastcancercare.org.uk/sites/default/files/publications/pdf/bcc66_younger_women_with_breast_cancer_web.pdf",
                        "title": "Younger women with breast cancer",
                        "description": "This booklet looks at the different issues, feelings and experiences you may have as a younger woman diagnosed with primary breast cancer. This is breast cancer that has not spread beyond the breast or the lymph nodes (glands) under the arm (axilla)."
                    },
                    {
                        "link": "https://www.usatoday.com/story/news/nation/2013/02/26/breast-cancers-young-women/1949157/",
                        "title": "Deadly breast cancers are rising in young women",
                        "description": "At a time when the USA is making progress overall against cancer, a new study documents a worrisome rise in the number of young women diagnosed with advanced, incurable breast cancer."
                    },
                    {
                        "link": "https://breast-cancer-research.biomedcentral.com/articles/10.1186/bcr2647",
                        "title": "Breast cancer in young women | Breast Cancer Research",
                        "description": "Although uncommon, breast cancer in young women is worthy of special attention due to the unique and complex issues that are raised. This article reviews specific challenges associated with the care of younger breast cancer patients, which include fertility preservation, management of inherited breast cancer syndromes, maintenance of bone health, secondary prevention, and attention to psychosocial issues."
                    },
                    {
                        "link": "https://www.medicinenet.com/breast_cancer_in_young_women/article.htm",
                        "title": "Breast Cancer in Young Women: What's the Prognosis",
                        "description": "Breast Cancer in Young Women"
                    },
                    {
                        "link": "http://www.ascopost.com/issues/may-25-2017/unique-challenges-facing-young-women-with-breast-cancer/",
                        "title": "Unique Challenges Facing Young Women With Breast Cancer - The ASCO Post",
                        "description": "Unique Challenges Facing Young Women With Breast Cancer - The ASCO Post"
                    },
                    {
                        "link": "http://www.dana-farber.org/young-and-strong-program-for-young-women-with-breast-cancer/",
                        "title": "Young and Strong Program for Young Women with Breast Cancer - Dana-Farber Cancer Institute | Boston, MA",
                        "description": "Dana-Farber Cancer Institute program for young women with breast cancer provides focused treatment, care and counseling for younger breast cancer patients."
                    }
                ],
                "blogs_and_posts": [
                    {
                        "link": "http://www.flare.com/health/young-women-with-breast-cancer/",
                        "title": "7 Young Women with Breast Cancer Share Their Stories - FLARE",
                        "description": "Fertility, body image, even being taken seriously at the doctor's office... young women with breast cancer tell FLARE what it's really like"
                    },
                    {
                        "link": "https://www.youngsurvival.org/blog/survivor-stories/survivor/jennifer",
                        "title": "Jennifer | Young Survival Coalition, Young women facing breast cancer together.",
                        "description": "I don't want to identify myself with anything cancer. Yes, it happened to me but no, it is not a part of who I am. Like any other negative experience in your life, you get through it, you learn from it, and you move on."
                    },
                    {
                        "link": "http://youngwomensbreastcancerblog.blogspot.com/",
                        "title": "Young Women's Breast Cancer Blog UK",
                        "description": "Young Women's Breast Cancer Blog UK"
                    },
                    {
                        "link": "http://www.butdoctorihatepink.com/",
                        "title": "Breast Cancer? But Doctor....I hate pink!",
                        "description": "Living with incurable, metastatic breast cancer."
                    },
                    {
                        "link": "http://www.letlifehappen.com/",
                        "title": "Breast Cancer - Cancer - Metastatic Breast Cancer - Patient",
                        "description": "Barbara Jacoby is an award winning blogger that has contributed her two time Breast Cancer journey, patient advocacy mission and Domestic Abuse experience"
                    },
                    {
                        "link": "http://carolinemfr.blogspot.com/",
                        "title": "Caroline's Breast Cancer Blog",
                        "description": "Caroline's Breast Cancer Blog"
                    },
                    {
                        "link": "http://nancyspoint.com/",
                        "title": "Nancy's Point | A blog about breast cancer, loss & survivorship",
                        "description": "A blog about breast cancer, loss & survivorship"
                    },
                    {
                        "link": "http://www.tamiboehmer.com/",
                        "title": "Tami Boehmer",
                        "description": "Tami Boehmer"
                    },
                    {
                        "link": "https://perksofcancer.com/",
                        "title": "The Perks of Having Cancer! | Follow Florence's Challenge To Find 100 Perks Of Having Cancer.",
                        "description": "Follow Florence's Challenge To Find 100 Perks Of Having Cancer."
                    },
                    {
                        "link": "http://www.beautythroughthebeast.com/blog",
                        "title": "BLOG — BEAUTY THROUGH THE BEAST  ",
                        "description": "A fashion minded-blog written by a young woman fighting breast cancer. "
                    }
                ],
                "pubmed": [
                    {
                        "link": "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4303229/",
                        "title": "Biology of breast cancer in young women",
                        "description": "Breast cancer arising at a young age is relatively uncommon, particularly in the developed world. Several studies have demonstrated that younger patients often experience a more aggressive disease course and have poorer outcome compared to older women"
                    },
                    {
                        "link": "https://www.ncbi.nlm.nih.gov/pubmed/24074783",
                        "title": "Management of breast cancer in very young women.  - PubMed - NCBI",
                        "description": "Breast. 2013 Aug;22 Suppl 2:S176-9. doi: 10.1016/j.breast.2013.07.034. Comparative Study; Review"
                    },
                    {
                        "link": "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3695538/",
                        "title": "Epidemiology and prognosis of breast cancer in young women",
                        "description": "Breast cancer is the most common malignancy in women with 6.6% of cases diagnosed in young women below the age of 40. Despite variances in risk factors, Age Standardized Incidence Rates of breast cancer in young women vary little between different countries"
                    },
                    {
                        "link": "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4694614/",
                        "title": "Managing breast cancer in younger women: challenges and solutions",
                        "description": "Breast cancer in young women is relatively rare compared to breast cancer occurring in older women. Younger women diagnosed with breast cancer also tend to have a more aggressive biology and consequently a poorer prognosis than older women. In addition,"
                    },
                    {
                        "link": "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC2894028/",
                        "title": "Breast Cancer Before Age 40 Years",
                        "description": "Approximately 7% of women with breast cancer are diagnosed before the age of 40 years, and this disease accounts for more than 40% of all cancer in women in this age group. Survival rates are worse when compared to those in older women, and multivariate"
                    },
                    {
                        "link": "https://www.ncbi.nlm.nih.gov/pubmed/28260181",
                        "title": "Breast cancer in young women: an overview.  - PubMed - NCBI",
                        "description": "Updates Surg. 2017 Sep;69(3):313-317. doi: 10.1007/s13304-017-0424-1. Epub  2017 Mar 4. Review"
                    },
                    {
                        "link": "https://www.ncbi.nlm.nih.gov/pubmed/17059343",
                        "title": "Breast cancer in young women: prognostic factors and clinicopathological features.  - PubMed - NCBI",
                        "description": "Asian Pac J Cancer Prev. 2006 Jul-Sep;7(3):451-4. Research Support, Non-U.S. Gov't"
                    },
                    {
                        "link": "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC2770847/",
                        "title": "Breast Cancer in Young Women: Poor Survival Despite Intensive Treatment",
                        "description": "Breast cancer is uncommon in young women and correlates with a less favourable prognosis; still it is the most frequent cancer in women under 40, accounting for 30–40% of all incident female cancer. The aim of this study was to study prognosis"
                    },
                    {
                        "link": "https://www.ncbi.nlm.nih.gov/pubmed/18501818",
                        "title": "Breast cancer in young women.  - PubMed - NCBI",
                        "description": "J Am Coll Surg. 2008 Jun;206(6):1193-203. doi: 10.1016/j.jamcollsurg.2007.12.026. Epub  2008 Apr 24. Review"
                    },
                    {
                        "link": "https://www.ncbi.nlm.nih.gov/pubmed/27479041",
                        "title": "Breast cancer in young women: Pathologic features and molecular phenotype.  - PubMed - NCBI",
                        "description": "Breast. 2016 Oct;29:109-16. doi: 10.1016/j.breast.2016.07.007. Epub  2016 Jul 29. Multicenter Study"
                    }
                ],
                "news_articles": [
                    {
                        "link": "http://www.sacbee.com/news/local/health-and-medicine/article108330857.html",
                        "title": "More younger women are receiving breast cancer diagnoses | The Sacramento Bee",
                        "description": "Growing numbers of women under 40 are receiving breast cancer diagnoses. The disease often proves more aggressive in younger women, many of whom are less financially able to weather the heavy burden of treatment and recovery."
                    },
                    {
                        "link": "https://www.statnews.com/2017/08/29/double-mastectomy-breast-cancer/",
                        "title": "Why are more and more women opting for double mastectomy?",
                        "description": "Even as cancer treatments have become increasingly targeted, a growing number of women with cancer in one breast are opting for a double mastectomy."
                    },
                    {
                        "link": "https://economictimes.indiatimes.com/magazines/panache/breast-cancer-rates-are-on-the-rise-among-young-women-and-heres-how-you-can-prevent-it/articleshow/62803645.cms",
                        "title": "Breast cancer rates are on the rise among young women and here's how you can prevent it - The Economic Times",
                        "description": "It is the most common cancer in most parts of India, both urban and rural."
                    },
                    {
                        "link": "http://www.columbian.com/news/2018/jan/22/breast-cancer-surgeon-diagnosed-with-breast-cancer-advocates-oncoplastic-surgery/",
                        "title": "Breast cancer surgeon diagnosed with breast cancer advocates oncoplastic surgery | The Columbian",
                        "description": 'Breast cancer surgeon diagnosed with breast cancer advocates oncoplastic surgery | The Columbian'
                    },
                    {
                        "link": "https://www.thesun.ie/fabulous/2044496/young-irish-mum-urges-women-to-be-aware-of-breast-cancer-after-being-diagnosed-with-condition-at-32-and-seven-months-after-giving-birth/",
                        "title": "Young Irish mum urges women to be aware of breast cancer after being diagnosed with condition at 32 and seven months after giving birth",
                        "description": "Having breastfed her baby and with no history of the condition in her family, Georgie Crawford told how she never expected to face the disease"
                    },
                    {
                        "link": "http://www.jamaicaobserver.com/your-health-your-wealth/breast-cancer_122442?profile=1373",
                        "title": "Breast cancer gene does not boost risk of death — study",
                        "description": "PARIS, France (AFP) —Young women with the breast cancer gene mutation that prompted..."
                    },
                    {
                        "link": "https://www.medicalnewstoday.com/articles/320387.php",
                        "title": "Breast cancer: These gene variations may shorten young women's survival",
                        "description": "New research finds that young women with early-onset breast cancer possess variations in a specific gene that might affect their survival."
                    },
                    {
                        "link": "https://www.forbes.com/sites/elaineschattner/2017/12/07/in-young-women-kisqali-slows-metastatic-breast-cancer-and-relieves-symptoms/",
                        "title": "In Young Women With Metastatic Breast Cancer, Kisqali Delays Tumor Growth And Relieves Symptoms",
                        "description": "So far in this trial, ribociclib extended PFS by around a year (23.8 vs. 13.0 months). That’s a dramatic and early result."
                    },
                    {
                        "link": "http://people.com/human-interest/young-women-breast-cancer/",
                        "title": "22-Year-Old Discovers Breast Cancer Lump After Dropping Necklace | PEOPLE.com",
                        "description": "\"I spent the whole weekend borderline freaking out, and then thinking there was just no way that this could happen,\" Leslie Almiron tells PEOPLE"
                    },
                    {
                        "link": "http://www.healthimaging.com/topics/womens-health/breast-imaging/bi-annual-mris-more-effective-mammograms-high-risk-young-women",
                        "title": "Bi-annual MRI more effective than mammograms for high-risk young women | Health Imaging",
                        "description": "A new study conducted by researchers from the University of Chicago Medicine and the University of Washington, Seattle has demonstrated that young women at a genetically high risk of developing breast cancer would benefit more receiving bi-annual MRI exams rather than standard annual mammogram."
                    }
                ]
            }
        elif dd.get('age') > 70:
            data = {
                "google_links": [
                    {
                        "link": "http://www.breastcancer.org/research-news/20120207",
                        "title": "Women Older Than 65 Have Worse Outcomes After Breast Cancer Diagnosis",
                        "description": "Women Older Than 65 Have Worse Outcomes After Breast Cancer Diagnosis"
                    },
                    {
                        "link": "http://theoncologist.alphamedpress.org/content/15/suppl_5/57.full",
                        "title": "Coming of Age: Breast Cancer in Seniors ",
                        "description": "The Oncologist is a journal devoted to medical and practice issues for surgical, radiation, and medical oncologists."
                    },
                    {
                        "link": "http://ascopubs.org/doi/full/10.1200/jop.2015.010207",
                        "title": "Breast Cancer in Women Older Than 80 Years: Journal of Oncology Practice: Vol 12, No 2",
                        "description": 'Breast cancer is the most common cancer in women, with an incidence that rises dramatically with age. The average age at diagnosis of breast cancer is 61 years, and the majority of woman who die of breast cancer are age 65 years and older.'
                    },
                    {
                        "link": "https://www.everydayhealth.com/news/letting-go-radiation-older-women-with-breast-cancer/",
                        "title": "Letting Go of Radiation for Older Women With Breast Cancer | Everyday Health",
                        "description": "Patients who have early-stage breast cancer and are older than age 70 should discuss all options with their doctor before considering radiation."
                    },
                    {
                        "link": "https://www.medscape.com/viewarticle/817435",
                        "title": "Breast Cancer in the Elderly",
                        "description": "Geriatrician assessment can detect deficits that may affect chemotherapy tolerance, but is comprehensive geriatric assessment feasible in the oncology setting?"
                    },
                    {
                        "link": "https://www.health.harvard.edu/cancer/good-news-about-early-stage-breast-cancer-for-older-women",
                        "title": "Good news about early-stage breast cancer for older women - Harvard Health",
                        "description": "Older women have many options for breast cancer screening and treatment. They should make these decisions based on their health, life expectancy, and personal…"
                    },
                    {
                        "link": "https://www.omicsonline.org/open-access/treatment-of-breast-cancer-in-women-aged-80-and-older-a-systematic-review-.php?aid=82098",
                        "title": "Treatment of Breast Cancer in Women Aged 80 and Older | OMICS International",
                        "description": "Background: The elderly population is growing in the United States. Most clinical trials exclude patients over 80, therefore there is a paucity of data regarding the corr.."
                    },
                    {
                        "link": "https://www.aafp.org/afp/1998/1001/p1163.html",
                        "title": "Breast Cancer in Older Women - American Family Physician",
                        "description": "The American Geriatric Society currently recommends screening mammography for women up to 85 years of age whose life expectancy is three years or longer. The value of clinical breast examinations in older women needs further study."
                    },
                    {
                        "link": "https://www.sciencedirect.com/science/article/pii/S1507136712000831",
                        "title": "Breast cancer in the elderly—Should it be treated differently? - ScienceDirect",
                        "description": "Breast cancer in the elderly—Should it be treated differently? - ScienceDirect"
                    },
                    {
                        "link": "https://www.griswoldhomecare.com/blog/treatment-to-prognosis-breast-cancer-care-for-elderly-women/",
                        "title": "Treatment to Prognosis: Breast Cancer Care for Elderly Women | Griswold",
                        "description": "We provide everything you need to know about breast cancer in elderly women from prognosis to treatment options."
                    }
                ],
                "blogs_and_posts": [
                    {
                        "link": "http://blog.dana-farber.org/insight/2015/08/what-older-women-should-know-about-breast-cancer/",
                        "title": "What Older Women Should Know About Breast Cancer | Dana-Farber Cancer Institute",
                        "description": "American women have a 12 percent lifetime risk of being diagnosed with breast cancer, the second most common cancer in women. While young women do get breast cancer, the disease is much more common in women aged 60 and older. Rachel Freedman, MD, MPH, a medical oncologist at the Susan"
                    },
                    {
                        "link": "https://community.breastcancer.org/forum/104",
                        "title": "Breast Cancer Forum: Older Than 60 Years Old With Breast Cancer",
                        "description": "Breast Cancer Discussion Forums - Access the shared knowledge of thousands of people affected by breast cancer"
                    },
                    {
                        "link": "http://www.joanlunden.com/category/49-breast-cancer-home/item/122-i-have-breast-cancer",
                        "title": "I Have Breast Cancer | Joan Lunden",
                        "description": "I Have Breast Cancer | Joan Lunden"
                    },
                    {
                        "link": "https://medschool.duke.edu/about-us/news-and-communications/med-school-blog/older-breast-cancer-patients-defy-survival-models",
                        "title": "Older Breast Cancer Patients Defy Survival Models | Duke School of Medicine",
                        "description": "Older women with early-stage, invasive breast cancer had better survival rates than what was estimated by a popular online tool for predicting surv"
                    },
                    {
                        "link": "https://www.vitae-care.com/blog/breast-cancer-in-older-age",
                        "title": "Breast Cancer Creates Significant Emotional Strain on Elderly Women",
                        "description": "Breast cancer is more common among elderly than younger women. Treatment choices can be difficult because of factors related to age and reduced strength."
                    },
                    {
                        "link": "https://www.aplaceformom.com/senior-care-resources/articles/breast-cancer-in-seniors",
                        "title": "Breast Cancer and Seniors",
                        "description": "Read about breast cancer risks for senior citizens. Learn breast cancer detection methods, effects and treatments. Get a surgery and therapy overview."
                    },
                    {
                        "link": "http://www.lbbc.org/blog",
                        "title": "Blog | Living Beyond Breast Cancer",
                        "description": "If you want to read the latest breast cancer stories, studies, and news, as well as learn more about treatments, support, and side effects, visit our blog here."
                    },
                    {
                        "link": "https://cancer.osu.edu/blog/personalized-breast-cancer-treatment-for-older-women",
                        "title": "Personalized Breast Cancer Treatment for Older Women | OSUCCC - James",
                        "description": "Experts at The James are providing optimal treatments for older patients (who sometimes have multiple other medical challenges) and each patient receives an individualized treatment plan."
                    },
                    {
                        "link": "https://www.bcrf.org/blog/breast-cancer-elderly-how-bcrf-researchers-are-treating-growing-patient-population",
                        "title": "Breast Cancer in the Elderly: How BCRF Researchers are Treating this Growing Patient Population | BCRF",
                        "description": "Breast cancer is a disease of aging. The median age of breast cancer is 62 and around one quarter are women between ages 75-84, according to the Surveillance Epidemiology and End Results registry."
                    },
                    {
                        "link": "http://blog.thebreastcancersite.com/",
                        "title": "Chemo And Dry Mouth: A Dental Hygienist And Breast Cancer Survivor Shares Tips",
                        "description": "Chemo can wreak havoc on your body, especially your mouth. But there are ways to combat it."
                    }
                ],
                "pubmed": [
                    {
                        "link": "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3874410/",
                        "title": "Early breast cancer in the older woman",
                        "description": "reast cancer is a disease associated with aging; there is a rise in both breast cancer incidence and mortality with increasing age. With the aging of the US population, the number of older adults diagnosed with breast cancer and the number of breast"
                    },
                    {
                        "link": "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4500607/",
                        "title": "Management of early breast cancer in older women: from screening to treatment",
                        "description": "Breast cancer is a common condition. It is a leading cause of death among women, and its incidence increases with age. Aging of the population and improvement of the quality of life of elders make it a major public health issue. We reviewed the literature"
                    },
                    {
                        "link": "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4577665/",
                        "title": "The Treatment of Primary Breast Cancer in Older Women With Adjuvant Therapy",
                        "description": "Breast cancer is the most common cancer in women in Germany. Mortality from breast cancer has declined over the past 15 years, but less so in women aged 70 or older than in younger women. The discrepancy might be explained by age-related differences in"
                    },
                    {
                        "link": "https://www.ncbi.nlm.nih.gov/pubmed/25993142",
                        "title": "Management of older women with early-stage breast cancer.  - PubMed - NCBI",
                        "description": "Am Soc Clin Oncol Educ Book. 2015:48-55. doi: 10.14694/EdBook_AM.2015.35.48. Research Support, Non-U.S. Gov't"
                    },
                    {
                        "link": "https://www.ncbi.nlm.nih.gov/pubmed/1430878",
                        "title": "The biology of breast cancer in older women.  - PubMed - NCBI",
                        "description": "J Gerontol. 1992 Nov;47 Spec No:19-23. Research Support, U.S. Gov't, P.H.S.; Review"
                    },
                    {
                        "link": "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3745823/",
                        "title": "To screen or not to screen older women for breast cancer: a conundrum",
                        "description": "To screen or not to screen older women for breast cancer: a conundrum"
                    },
                    {
                        "link": "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC222918/",
                        "title": "Outcomes and quality of life following breast cancer treatment in older women: When, why, how much, and what do women want?",
                        "description": "There are few comprehensive reviews of breast cancer outcomes in older women. We synthesize data to describe key findings and gaps in knowledge about the outcomes of breast cancer in this population.We reviewed research published between 1995 and June"
                    },
                    {
                        "link": "https://www.ncbi.nlm.nih.gov/pubmed/14581426",
                        "title": "Breast cancer in older women: quality of life and psychosocial adjustment in the 15 months after diagnosis.  - PubMed - NCBI",
                        "description": "J Clin Oncol. 2003 Nov 1;21(21):4027-33. Multicenter Study; Research Support, Non-U.S. Gov't; Research Support, U.S. Gov't, P.H.S."
                    },
                    {
                        "link": "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4745843/",
                        "title": "Optimal breast cancer screening strategies for older women: current perspectives",
                        "description": "Breast cancer is a major cause of cancer-related deaths among older women, aged 65 years or older. Screening mammography has been shown to be effective in reducing breast cancer mortality in women aged 50–74 years but not among those aged 75 years"
                    },
                    {
                        "link": "https://www.ncbi.nlm.nih.gov/pubmed/17050874",
                        "title": "Postmastectomy radiation and survival in older women with breast cancer.  - PubMed - NCBI",
                        "description": "J Clin Oncol. 2006 Oct 20;24(30):4901-7. Research Support, N.I.H., Extramural"
                    }
                ],
                "news_articles": [
                    {
                        "link": "https://www.reuters.com/article/us-breast-cancer/breast-cancer-may-not-change-lifespan-for-older-women-idUSTRE72D7XU20110315",
                        "title": "Breast cancer may not change lifespan for older women | Reuters",
                        "description": "By Genevra PittmanNEW YORK (Reuters Health) - Older women who are diagnosed with early-stage breast cancer can expect to live just as long as peers without breast cancer, according to a new study"
                    },
                    {
                        "link": "https://medicalxpress.com/news/2018-02-family-history-breast-cancer-older.html",
                        "title": "Family history increases breast cancer risk in older women: Weighing screening options",
                        "description": "Family history of breast cancer continues to significantly increase chances of developing invasive breast tumors in aging women—those ages 65 and older, according to research published in JAMA Internal Medicine. The findings"
                    },
                    {
                        "link": "https://www.healio.com/internal-medicine/oncology/news/online/%7B04c3ab00-a29b-4f86-af55-9b6b906aa9db%7D/family-history-increases-breast-cancer-risk-regardless-of-age",
                        "title": "Family history increases breast cancer risk regardless of age",
                        "description": "First-degree family history was associated with a significantly increased risk for invasive breast cancer among older women regardless of a relative&rsquo;s age atdiagnosis, according to a study published in JAMA Internal Medicine.Another study, also published in JAMA Internal Medicine, revealed that women with and without a personal history of breast cancer who undergo screening via MRI "
                    },
                    {
                        "link": "http://www.dailymail.co.uk/news/article-5374323/Patients-breast-cancer-live-longer-soft-chemo.html",
                        "title": "Patients with breast cancer live longer with soft chemo  | Daily Mail Online",
                        "description": "Traditional chemotherapy drugs can cause such severe side effects that they are often not given to older people in the late stages of cancer."
                    },
                    {
                        "link": "https://www.deccanchronicle.com/lifestyle/health-and-wellbeing/270118/older-women-with-high-body-fat-at-increased-risk-of-breast-cancer-stu.html",
                        "title": "Older women with high body fat at increased risk of breast cancer: Study",
                        "description": "Body fat levels are typically measured via BMI, which is a ratio of weight to height."
                    },
                    {
                        "link": "https://www.eurekalert.org/pub_releases/2018-01/wkh-dbr013018.php",
                        "title": "Direct-to-implant breast reconstruction provides good results in older women | EurekAlert! Science News",
                        "description": "For older women undergoing mastectomy for breast cancer, direct-to-implant (DTI) breast reconstruction provides good outcomes in a single-step procedure, while avoiding some of the inconvenience and risks of staged approaches to breast reconstruction, reports a study in the February issue of Plastic and Reconstructive Surgery®, the official medical journal of the American Society of Plastic Surgeons (ASPS)."
                    },
                    {
                        "link": "https://medicalxpress.com/news/2018-02-soft-chemotherapy-effective-older-patients.html",
                        "title": "Soft chemotherapy is very effective in older patients when added to targeted treatment in aggressive breast cancer",
                        "description": "Avoidance of side-effects of chemotherapy is particularly important in the elderly, but finding the balance between reduced toxicity and maximum effectiveness is not always easy. A trial carried out by the European Organisation"
                    },
                    {
                        "link": "http://www.pharmacytimes.com/publications/health-system-edition/2018/january2018/breast-cancer-the-clinicians-involvement",
                        "title": "Breast Cancer: the Clinician's Involvement",
                        "description": "For many women, the fear of breast cancer is always present."
                    },
                    {
                        "link": "https://www.irishtimes.com/life-and-style/health-family/after-cancer-relapse-is-the-biggest-fear-but-not-the-only-risk-1.3381974",
                        "title": "After cancer: Relapse is the biggest fear, but not the only risk",
                        "description": "Cancer survivors can face post-traumatic stress and a higher risk of heart failure"
                    },
                    {
                        "link": "https://scroll.in/pulse/868165/while-fighting-breast-cancer-one-woman-also-fought-to-keep-her-breast",
                        "title": "The difficult choice of keeping or removing a cancer-stricken breast",
                        "description": "For some women with breast cancer, a mastectomy may seem the best option. For others, the idea of losing a breast is too terrible."
                    }
                ]
            }
        else:
            data = {
                "google_links": [
                    {
                        "link": "http://www.breastcancer.org/",
                        "title": "Breastcancer.org - Breast Cancer Information and Awareness",
                        "description": "We are a 501(c) non-profit organization offering a complete resource for breast cancer, including up-to-date information on the latest treatments, screening tests, stages and breast cancer types, as well as prevention information. "
                    },
                    {
                        "link": "https://www.mayoclinic.org/diseases-conditions/breast-cancer/symptoms-causes/syc-20352470",
                        "title": "Breast cancer - Symptoms and causes - Mayo Clinic",
                        "description": 'Breast cancer — Comprehensive overview covers prevention, symptoms, diagnosis and treatment of breast cancer.'
                    },
                    {
                        "link": "https://www.medicalnewstoday.com/articles/37136.php",
                        "title": "Breast cancer: Symptoms, risk factors, and treatment",
                        "description": "Breast cancer is a common cancer in women, but screening and therapy now make it treatable in many cases. Learn more about risk factors and treatment. "
                    },
                    {
                        "link": "https://www.cancer.org/cancer/breast-cancer.html",
                        "title": "Breast Cancer",
                        "description": "Get detailed information about breast cancer risks, causes, symptoms, treatments, and more from the American Cancer Society."
                    },
                    {
                        "link": "https://en.wikipedia.org/wiki/Breast_cancer",
                        "title": "Breast cancer",
                        "description": 'Breast cancer - Wikipedia'
                    },
                    {
                        "link": "https://medlineplus.gov/breastcancer.html",
                        "title": "Breast Cancer | Breast Cancer Symptoms | MedlinePlus",
                        "description": "Breast cancer affects 1 in 8 women during their lives. Here's what you need to know about risk factors, symptoms, diagnosis, and treatment."
                    },
                    {
                        "link": "http://www.health.com/breast-cancer",
                        "title": "Breast Cancer: Symptoms, Causes, Types and Treatment - Health.com",
                        "description": "What is breast cancer? Learn about the signs and symptoms, types and stages and treatment options available for breast cancer."
                    },
                    {
                        "link": "https://www.cancer.gov/types/breast",
                        "title": "Breast Cancer—Patient Version - National Cancer Institute",
                        "description": "Information about breast cancer treatment, prevention, genetics, causes, screening, clinical trials, research and statistics from the National Cancer Institute."
                    },
                    {
                        "link": "http://www.nationalbreastcancer.org/breast-cancer-facts",
                        "title": "Breast Cancer Facts - National Breast Cancer Foundation",
                        "description": "Get the facts about breast cancer, including what it is, how many people are diagnosed each year, and how many people will develop it within their lifetime."
                    },
                    {
                        "link": "http://www.nationalbreastcancer.org/",
                        "title": "Information, Awareness & Donations - National Breast Cancer Foundation",
                        "description": "National Breast Cancer Foundation provides early detection screenings, including mammograms, breast health education, and a supportive community."
                    }
                ],
                "blogs_and_posts": [
                    {
                        "link": "http://hormonenegative.blogspot.com/",
                        "title": "Positives About Negative",
                        "description": 'Hope and help for triple-negative (TNBC) and  other forms of hormone-negative breast cancer.'
                    },
                    {
                        "link": "http://www.lbbc.org/blog",
                        "title": "Blog | Living Beyond Breast Cancer",
                        "description": "If you want to read the latest breast cancer stories, studies, and news, as well as learn more about treatments, support, and side effects, visit our blog here."
                    },
                    {
                        "link": "https://breastcancer-news.com/blog/2016/07/13/dealing-with-breast-cancer-diagnosis/",
                        "title": "Wide Awake at 4 a.m.: Dealing with a Breast Cancer Diagnosis",
                        "description": "Read Nancy Briar's blog post about the fear, questions, and uncertainties that comes with being diagnosed with breast cancer."
                    },
                    {
                        "link": "http://mywifesfightwithbreastcancer.com/blog/",
                        "title": "Blog — The Battle We Didn't Choose",
                        "description": "My late wife, Jennifer, was diagnosed with breast cancer in 2008, five months after our wedding, and she died on December 22, 2011. Thankfully Jennifer allowed me to photograph of day to day life. Our hope was that we could provide a better understanding of the reality of life with cancer."
                    },
                    {
                        "link": "http://carolinemfr.blogspot.com/",
                        "title": "Caroline's Breast Cancer Blog",
                        "description": 'Caroline\'s Breast Cancer Blog'
                    },
                    {
                        "link": "https://www.blogforacure.com/members.php?type=breast+cancer",
                        "title": "398 Breast Cancer Blogs ",
                        "description": '398 Breast Cancer survivors blogging about their experience. Find hope, strength and courage through this supporting and caring Breast Cancer community.'
                    },
                    {
                        "link": "http://liz.oriordan.co.uk/",
                        "title": "Breast Surgeon with Breast Cancer",
                        "description": "Liz O'Riordan, a Consultant Breast Surgeon blogs about her own unique experiences of breast cancer, including chemotherapy and reconstruction, to help both doctors and patients understand what it's really like"
                    },
                    {
                        "link": "https://michelle-giannino.squarespace.com/",
                        "title": "Stupid Dumb Breast Cancerstupid dumb breast cancer",
                        "description": "stupid dumb breast cancer"
                    },
                    {
                        "link": "https://www.breastcancercare.org.uk/information-support/vita-magazine/blog",
                        "title": "Vita blog",
                        "description": "Packed full of inspiring stories told by incredible people, our Vita blog is the place to be to read first hand accounts of the brave people living with breast cancer in the UK."
                    },
                    {
                        "link": "http://www.nalie.ca/",
                        "title": "The Diary of Nalie",
                        "description": "The Diary of a Metastatic Breast Cancer Thriver."
                    }
                ],
                "pubmed": [
                    {
                        "link": "https://www.ncbi.nlm.nih.gov/pubmedhealth/PMH0001911/",
                        "title": "Breast Cancer - National Library of Medicine - PubMed Health",
                        "description": "Cancer that forms in tissues of the breast."
                    },
                    {
                        "link": "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3255438/",
                        "title": "VARIOUS TYPES AND MANAGEMENT OF BREAST CANCER: AN OVERVIEW",
                        "description": 'Now days, breast cancer is the most frequently diagnosed life-threatening cancer in women and the leading cause of cancer death among women. Since last two decades, researches related to the breast cancer has lead to extraordinary progress in our understanding ...'
                    },
                    {
                        "link": "https://www.ncbi.nlm.nih.gov/pubmedhealth/PMH0072606/",
                        "title": "Breast cancer: Overview - National Library of Medicine - PubMed Health",
                        "description": "Being diagnosed with breast cancer often makes people feel very frightened and anxious. But if you get breast cancer for the first time and it hasn’t spread far, there’s a good chance that treatment can lead to full recovery. There are also many support services that help people in everyday life, to return to work and cope emotionally with breast cancer."
                    },
                    {
                        "link": "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4135458/",
                        "title": "The breast cancer epidemic: 10 facts",
                        "description": 'Breast cancer, affecting one in eight American women, is a modern epidemic. The increasing frequency of breast cancer is widely recognized. However, the wealth of compelling epidemiological data on its prevention is generally not available, and as a consequence, ...'
                    },
                    {
                        "link": "https://www.ncbi.nlm.nih.gov/pubmed/15894099",
                        "title": "Breast cancer.  - PubMed - NCBI",
                        "description": "Lancet. 2005 May 14-20;365(9472):1727-41. Research Support, Non-U.S. Gov't; Review"
                    },
                    {
                        "link": "https://www.ncbi.nlm.nih.gov/pubmed/11902563",
                        "title": "Epidemiology of breast cancer.  - PubMed - NCBI",
                        "description": "Lancet Oncol. 2001 Mar;2(3):133-40. Research Support, Non-U.S. Gov't; Review"
                    },
                    {
                        "link": "https://www.ncbi.nlm.nih.gov/pubmed/16045991",
                        "title": "Aluminium, antiperspirants and breast cancer.  - PubMed - NCBI",
                        "description": "J Inorg Biochem. 2005 Sep;99(9):1912-9."
                    },
                    {
                        "link": "https://www.ncbi.nlm.nih.gov/pubmed/22990110",
                        "title": "Breast cancer metastasis.  - PubMed - NCBI",
                        "description": "Cancer Genomics Proteomics. 2012 Sep-Oct;9(5):311-20. Review"
                    },
                    {
                        "link": "https://www.ncbi.nlm.nih.gov/pubmed/17975657",
                        "title": "Breast cancer: origins and evolution.  - PubMed - NCBI",
                        "description": "J Clin Invest. 2007 Nov;117(11):3155-63. Research Support, N.I.H., Extramural; Research Support, Non-U.S. Gov't; Research Support, U.S. Gov't, Non-P.H.S.; Review"
                    },
                    {
                        "link": "https://www.ncbi.nlm.nih.gov/pubmed/21310842",
                        "title": "Invasive breast cancer.  - PubMed - NCBI",
                        "description": "J Natl Compr Canc Netw. 2011 Feb;9(2):136-222. Practice Guideline; Research Support, N.I.H., Extramural; Research Support, Non-U.S. Gov't"
                    }
                ],
                "news_articles": [
                    {
                        "link": "http://www.nytimes.com/2013/04/28/magazine/our-feel-good-war-on-breast-cancer.html?pagewanted=all",
                        "title": "Our Feel-Good War on Breast Cancer - NYTimes.com",
                        "description": "The battle to raise awareness has been won. So why arenâ more lives being saved?"
                    },
                    {
                        "link": "https://www.usatoday.com/story/news/2017/09/28/julia-louis-dreyfus-breast-cancer-announcement-just-latest-show-evolution-stigma-spotlight/707775001/",
                        "title": "Julia Louis-Dreyfus breast cancer news shows how far we've come",
                        "description": "I remember in the '80s when I couldn't say the word 'breast' in a public meeting, said a doctor."
                    },
                    {
                        "link": "http://time.com/4057310/breast-cancer-overtreatment/",
                        "title": "Why Doctors Are Rethinking Breast-Cancer Treatment | Time.com",
                        "description": "Too much chemo. Too much radiation. And way too many mastectomies"
                    },
                    {
                        "link": "https://www.healio.com/hematology-oncology/breast-cancer/news/in-the-journals/%7B2534af47-24ab-4366-bce9-f71f851ee40a%7D/residence-in-ethnic-enclaves-associated-with-reduced-breast-colorectal-cancer-risk-among-asians-hispanics",
                        "title": "Residence in ethnic enclaves associated with reduced breast, colorectal cancer risk among Asians, Hispanics",
                        "description": "Living in ethnically or racially segregated neighborhoods appeared associated with a reduced risk for breast and colorectal cancers among Asian or Hispanic patients, but an increased risk for cancers with infectious origins, study data showed."
                    },
                    {
                        "link": "http://scienceblog.cancerresearchuk.org/2017/10/12/5-persistent-myths-about-the-causes-of-breast-cancer/",
                        "title": "5 persistent myths about the causes of breast cancer - Cancer Research UK - Science blog",
                        "description": "The good news is there’s no reason to be concerned about deodorants, bras, plastics and milk when it comes to breast cancer risk."
                    },
                    {
                        "link": "https://www.statnews.com/2017/07/10/breast-cancer-chemotherapy/",
                        "title": "Chemotherapy before breast cancer surgery might fuel metastasis",
                        "description": "When breast cancer patients get chemotherapy before surgery, it can make remaining malignant cells spread to distant sites, a new study found."
                    },
                    {
                        "link": "https://www.nature.com/articles/d41586-017-08309-y",
                        "title": "Acupuncture in cancer study reignites debate about controversial technique",
                        "description": "Large study suggests acupuncture could help women stick with unpleasant cancer treatments."
                    },
                    {
                        "link": "https://www.statnews.com/2017/10/23/breast-cancer-radiation/",
                        "title": "Many breast cancer patients receive more radiation than needed",
                        "description": "Only 48 percent of eligible patients today get the shorter regimen, in spite of the added costs and inconvenience of the longer type, an analysis shows."
                    },
                    {
                        "link": "https://www.statnews.com/2017/08/29/double-mastectomy-breast-cancer/",
                        "title": "Why are more and more women opting for double mastectomy?",
                        "description": "Even as cancer treatments have become increasingly targeted, a growing number of women with cancer in one breast are opting for a double mastectomy."
                    },
                    {
                        "link": "https://www.dovepress.com/toxic-elements-as-biomarkers-for-breast-cancer-a-meta-analysis-study-peer-reviewed-article-CMAR",
                        "title": "Toxic elements as biomarkers for breast cancer: a meta-analysis study | CMAR",
                        "description": "Toxic elements as biomarkers for breast cancer: a meta-analysis study Leila Jouybari,1 Marzieh Saei Ghare Naz,2 Akram Sanagoo,1 Faezeh Kiani,3 Fatemeh Sayehmiri,4 Kourosh Sayehmiri,5 Ali Hasanpour Dehkordi6 1Nursing Research Center, Goletsan University of Medical Sciences"
                    },
                    {
                        "link": "http://www.citywatchla.com/index.php/neighborhood-politics-hidden/370-420-file-news/14594-is-cannabis-a-treatment-for-cancer",
                        "title": "Is Cannabis a Treatment for Cancer?",
                        "description": "Is Cannabis a Treatment for Cancer?"
                    },
                    {
                        "link": "http://www.nature.com/articles/nrclinonc.2017.143",
                        "title": "Short-term NAT reveals resistance | Nature Reviews Clinical Oncology",
                        "description": "Research Highlight"
                    }
                ]
            }

        return Response(data,
                        status=status.HTTP_200_OK)


class TestDataView(GenericAPIView):
    serializer_class = DiagnosisSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        serializer = self.get_serializer(data=request.query_params)

        serializer.is_valid(raise_exception=True)
        dd = dict(serializer.validated_data)

        age = json.dumps({'age': dd.get('age')})

        ethnicity = dd.get('ethnicity')

        if ethnicity == 'Caucasian':
            v_ethnicity = 'White'
        elif ethnicity == 'African American':
            v_ethnicity = 'Black'
        elif ethnicity == 'Asian':
            v_ethnicity = 'Asian or Pacific Islander'
        elif ethnicity == 'Other':
            v_ethnicity = 'Unknown'
        else:
            v_ethnicity = ethnicity

        is_radiation_therapy = 'No'  # Radiation Therapy

        # Recommended Treatment Plans

        ## Overall Plans

        try:
            import subprocess
            import ast
            import re
            regex = r"\((.*?)\)"

            # START SURGERY
            surgery_args = ','.join([dd.get('sex'),
                                     str(dd.get('age')),
                                     v_ethnicity,
                                     str(float(dd.get('tumor_grade', 'unk'))),
                                     dd.get('site'),
                                     dd.get('type'),
                                     dd.get('stage'),
                                     dd.get('region'),
                                     v_get_t_size_cm(
                                         dd.get('tumor_size_in_mm')),
                                     str(dd.get('number_of_tumors')),
                                     str(dd.get('num_pos_nodes'))])

            surgery_command_str = [settings.ML_PYTHON_PATH,
                                   settings.ML_COMMAND_FILE,
                                   surgery_args, 'Surgery']

            surgery_command = subprocess.Popen(surgery_command_str,
                                               stdout=subprocess.PIPE,
                                               stderr=subprocess.PIPE,
                                               cwd=settings.ML_COMMAND_DIR)
            surgery_output, err = surgery_command.communicate()

            # To-Do remove try-except
            try:
                surgery_response = ast.literal_eval(
                    re.search(regex,
                              str(surgery_output.decode('utf8'))).group())
            except:
                surgery_response = ()

            # END SURGERY

            # START CHEMO

            chemo_args = ','.join([
                str(dd.get('age')),
                v_ethnicity,
                str(float(dd.get('tumor_grade'))),
                dd.get('type'),
                dd.get('stage'),
                dd.get('region'),
                v_get_t_size_cm(dd.get('tumor_size_in_mm')),
                str(dd.get('number_of_tumors')),
                str(dd.get('num_pos_nodes')),
                str(dd.get('er_status')),
                str(dd.get('pr_status')),
                str(dd.get('her2_status'))])

            chemo_command_str = [settings.ML_PYTHON_PATH,
                                 settings.ML_COMMAND_FILE,
                                 chemo_args, 'Chemo']

            chemo_command = subprocess.Popen(chemo_command_str,
                                             stdout=subprocess.PIPE,
                                             stderr=subprocess.PIPE,
                                             cwd=settings.ML_COMMAND_DIR)
            chemo_output, err = chemo_command.communicate()

            chemo_response = ast.literal_eval(
                re.search(regex, str(chemo_output.decode('utf8'))).group())

            # END CHEMO

            # START RADIATION

            import copy

            radiation_args = [
                str(dd.get('age')),
                v_ethnicity,
                str(float(dd.get('tumor_grade'))),
                dd.get('site'),
                dd.get('type'),
                dd.get('stage'),
                dd.get('region'),
                v_get_t_size_cm(dd.get('tumor_size_in_mm')),
                str(dd.get('number_of_tumors')),
                str(dd.get('num_pos_nodes')),
                str(dd.get('er_status')),
                str(dd.get('pr_status')),
                str(dd.get('her2_status'))]

            sm_radiation_args = copy.deepcopy(
                radiation_args)  # Copy base list of args

            sm_radiation_args.append('Mastectomy')
            sm_radiation_args.append(chemo_response[0])

            sm_radiation_command_str = [settings.ML_PYTHON_PATH,
                                        settings.ML_COMMAND_FILE,
                                        ','.join(sm_radiation_args),
                                        'Radiation']

            sm_radiation_command = subprocess.Popen(sm_radiation_command_str,
                                                    stdout=subprocess.PIPE,
                                                    stderr=subprocess.PIPE,
                                                    cwd=settings.ML_COMMAND_DIR)

            sm_radiation_output, err = sm_radiation_command.communicate()

            sm_radiation_response = ast.literal_eval(
                re.search(regex,
                          str(sm_radiation_output.decode('utf8'))).group())

            sl_radiation_args = copy.deepcopy(
                radiation_args)  # Copy base list of args

            sl_radiation_args.append('Lumpectomy')
            sl_radiation_args.append(chemo_response[0])

            sl_radiation_command_str = [settings.ML_PYTHON_PATH,
                                        settings.ML_COMMAND_FILE,
                                        ','.join(sm_radiation_args),
                                        'Radiation']

            sl_radiation_command = subprocess.Popen(sl_radiation_command_str,
                                                    stdout=subprocess.PIPE,
                                                    stderr=subprocess.PIPE,
                                                    cwd=settings.ML_COMMAND_DIR)
            sl_radiation_output, err = sl_radiation_command.communicate()

            sl_radiation_response = ast.literal_eval(
                re.search(regex,
                          str(sl_radiation_output.decode('utf8'))).group())

            # END RADIATION

            overall_plans = []

            surgery_level = round(surgery_response[1] * 100)
            chemo_level = round(chemo_response[1] * 100)
            sm_radiation_level = round(sm_radiation_response[1] * 100)
            sl_radiation_level = round(sl_radiation_response[1] * 100)

            if surgery_response[0] == 'Mastectomy':
                is_radiation_therapy = sm_radiation_response[0]
                overall_plans.append({
                    'name': 'Preferred Outcome A',
                    'type': surgery_response[0],
                    'radiation': 'Y' if sm_radiation_response[
                                            0] == 'Yes' else 'N',
                    'radiation_confidence_level': sm_radiation_level,
                    'chemo': 'Y' if chemo_response[0] == 'Yes' else 'N',
                    'chemo_confidence_level': chemo_level,
                    'surgery': 'Y',
                    'surgery_confidence_level': surgery_level,
                    'level': surgery_level})
                overall_plans.append({
                    'name': 'Preferred Outcome B',
                    'type': 'Lumpectomy',
                    'radiation': 'Y' if sl_radiation_response[
                                            0] == 'Yes' else 'N',
                    'radiation_confidence_level': sl_radiation_level,
                    'chemo': 'Y' if chemo_response[0] == 'Yes' else 'N',
                    'chemo_confidence_level': chemo_level,
                    'surgery': 'Y',
                    'surgery_confidence_level': 100 - surgery_level,
                    'level': 100 - surgery_level})
            else:
                is_radiation_therapy = sl_radiation_response[0]
                overall_plans.append({
                    'name': 'Preferred Outcome A',
                    'type': surgery_response[0],
                    'radiation': 'Y' if sl_radiation_response[
                                            0] == 'Yes' else 'N',
                    'radiation_confidence_level': sl_radiation_level,
                    'chemo': 'Y' if chemo_response[0] == 'Yes' else 'N',
                    'chemo_confidence_level': chemo_level,
                    'surgery_confidence_level': surgery_level,
                    'surgery': 'Y',
                    'level': surgery_level})
                overall_plans.append({
                    'name': 'Preferred Outcome B',
                    'type': 'Mastectomy',
                    'radiation': 'Y' if sm_radiation_response[
                                            0] == 'Yes' else 'N',
                    'radiation_confidence_level': sm_radiation_level,
                    'chemo': 'Y' if chemo_response[0] == 'Yes' else 'N',
                    'chemo_confidence_level': chemo_level,
                    'surgery_confidence_level': 100 - surgery_level,
                    'surgery': 'Y',
                    'level': 100 - surgery_level})
        except Exception as e:
            overall_plans = []

        # Hormonal Therapy

        hormonal_therapy = []
        if dd.get('pr_status') == '+' or dd.get('er_status') == '+':
            hormonal_therapy.append({'name': 'Tamoxifen',
                                     'number_of_treatments': 120,
                                     'administration': 'Monthly'})

        # Radiation Therapy

        radiation_therapy = []
        if is_radiation_therapy == 'Yes':
            radiation_therapy.append({'name': 'Beam Radiation',
                                      'number_of_treatments': 30,
                                      'administration': 'Daily'})

        # Chemo Therapy

        data = {
            'recommended_treatment_plans': {
                'overall_plans': overall_plans,
                'hormonal_therapy': hormonal_therapy,
                'radiation_therapy': radiation_therapy,
            },
            'percent_women_annualy_diagnosed': percent_women_annualy_diagnosed(
                age),
            'percent_women_by_type': percent_women_by_type(),
            'breast_cancer_by_grade_and_size': {
                'grade': breast_cancer_by_grade(age),
                'size': breast_cancer_by_size(age)
            },
            'distribution_of_stage_of_cancer': {
                'overall': distribution_of_stage_of_cancer(age),
                'by_race':
                    distribution_of_stage_of_cancer(
                        json.dumps({'age': dd.get('age'),
                                    'ethnicity': ethnicity},
                                   ensure_ascii=False)),
            },
            'percent_of_women_with_cancer_by_race': {
                'overall': percent_of_women_with_cancer_by_race_overall()
            },
            'surgery_decisions': surgery_decisions(age),
            'chemotherapy': {
                'overall': chemotherapy(age),
            },
            'radiation': {
                'overall': radiation(age),
            },
            'breast_cancer_by_state': breast_cancer_by_state(),
            'breast_cancer_at_a_glance': breast_cancer_at_a_glance(),
            'breast_cancer_by_age': breast_cancer_by_age(),
        }

        data['chemotherapy']['breakout_by_stage'] = breakout_by_stage(
            json.dumps({
                'age': dd.get('age'),
                'chemo': 'Yes',
                "breast-adjusted-ajcc-6th-stage-1988": {
                    "$in": ["I", "IIA", "IIB", "IIIA",
                            "IIIB", "IIIC", "IIINOS", "IV",
                            0]
                }}, ensure_ascii=False))

        data['radiation']['breakout_by_stage'] = breakout_by_stage(json.dumps({
            'age': dd.get('age'),
            'radiation': 'Yes',
            "breast-adjusted-ajcc-6th-stage-1988": {
                "$in": ["I", "IIA", "IIB", "IIIA",
                        "IIIB", "IIIC", "IIINOS", "IV",
                        0]
            }}, ensure_ascii=False))

        data['percent_of_women_with_cancer_by_race'][
            'by_age'] = percent_race_with_cancer_by_age(json.dumps({
            'age': dd.get('age'),
            'sex': 'Female'
        }, ensure_ascii=False))

        dd.pop('laterality', None)
        dd.pop('site', None)
        dd.pop('type', None)
        dd.pop('stage', None)
        dd.pop('number_of_tumors', None)
        dd.pop('region', None)

        similar_diagnosis = diagnosis(json.dumps(dd, ensure_ascii=False),
                                      limit=20)

        if len(similar_diagnosis) < 20:
            dd.pop('tumor_size_in_mm', None)
            similar_diagnosis = diagnosis(json.dumps(dd, ensure_ascii=False),
                                          limit=20)

            if len(similar_diagnosis) < 20:
                dd.pop('race', None)
                similar_diagnosis = diagnosis(
                    json.dumps(dd, ensure_ascii=False), limit=20)

                if len(similar_diagnosis) < 20:
                    dd.pop('age', None)
                    similar_diagnosis = diagnosis(
                        json.dumps(dd, ensure_ascii=False), limit=20)

        data['similar_diagnosis'] = similar_diagnosis

        return Response(data, status=status.HTTP_200_OK)
