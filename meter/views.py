from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action, api_view
from .models import Meter, MeterAssignment, MeterData
from .serializers import MeterSerializer, MeterAssignmentSerializer, MeterDataSerializer
from accounts.models import User
from django.core.exceptions import ValidationError
from django.http import HttpResponse
import pandas as pd
from io import BytesIO
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.urls import reverse
from django.utils import timezone
import os

class MeterViewSet(viewsets.ModelViewSet):
    """
    API endpoints for managing meters.
    """
    queryset = Meter.objects.all()
    serializer_class = MeterSerializer
    http_method_names = ['get', 'post', 'put', 'patch', 'delete']
    lookup_field = 'device_id'

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response({
                "details": {
                    "message": "Meter retrieved successfully",
                    "data": serializer.data
                }
            })
        except Exception as e:
            return Response({
                "error": "Error retrieving meter",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def create(self, request, *args, **kwargs):
        try:
            print("Received POST request:", request.data)
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response({
                "details": {
                    "message": "Meter created successfully",
                    "data": serializer.data
                }
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({
                "error": "Error creating meter",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            device_id = instance.device_id
            self.perform_destroy(instance)
            return Response({
                "details": {
                    "message": f"Meter with device ID '{device_id}' was successfully deleted"
                }
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "error": "Error deleting meter",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update(self, request, *args, **kwargs):
        try:
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response({
                "details": {
                    "message": "Meter updated successfully",
                    "data": serializer.data
                }
            })
        except Exception as e:
            return Response({
                "error": "Error updating meter",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def perform_update(self, serializer):
        """Custom perform_update method"""
        serializer.save()


class MeterAssignmentViewSet(viewsets.ViewSet):
    def list(self, request):
        try:
            assignments = MeterAssignment.objects.all()
            serializer = MeterAssignmentSerializer(assignments, many=True)
            return Response({
                "details": {
                    "message": "Meter assignments retrieved successfully",
                    "data": serializer.data
                }
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "error": "Error retrieving meter assignments",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def create(self, request):
        serializer = MeterAssignmentSerializer(data=request.data)
        if serializer.is_valid():
            try:
                assignment = serializer.save()
                return Response({
                    "details": {
                        "message": "Meter assignment created successfully",
                        "data": MeterAssignmentSerializer(assignment).data
                    }
                }, status=status.HTTP_201_CREATED)
            except ValidationError as e:
                return Response({
                    "error": "Validation error",
                    "details": e.message_dict if hasattr(e, 'message_dict') else {"detail": list(e)}
                }, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({
                    "error": "Error creating meter assignment",
                    "details": str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({
                "error": "Validation failed",
                "details": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk):
        try:
            assignment_id = pk
            if not assignment_id:
                return Response({
                    "error": "Assignment ID is required"
                }, status=status.HTTP_400_BAD_REQUEST)
            assignment = MeterAssignment.objects.get(id=assignment_id)
            assignment.delete()
            return Response(
                {
                    "details": {
                        "message": "Meter assignment deleted successfully"
                    }
                },status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "error": "Error deleting meter assignment",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MeterDataViewSet(viewsets.ViewSet):
    """
    API endpoints for managing meter data.
    """

    def list(self, request):
        """Get all meter data or filter by meter_id"""
        try:
            meter_id = request.query_params.get('meter_id', None)
            if meter_id:
                meter = get_object_or_404(Meter, device_id=meter_id)
                data_points = MeterData.objects.filter(meter=meter)
            else:
                data_points = MeterData.objects.all()

            serializer = MeterDataSerializer(data_points, many=True)
            return Response({
                "details": {
                    "message": "Meter data retrieved successfully",
                    "data": serializer.data
                }
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "error": "Error retrieving meter data",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def retrieve(self, request, pk=None):
        """Get a specific meter data point by ID"""
        try:
            print(f"Attempting to retrieve meter data with pk={pk}")
            data = MeterData.objects.filter(meter=pk).first()
            print(f"Found data: {data}")
            # This will never execute since get_object_or_404 raises an exception if not found
            if not data:
                print("Data is None - this line should never be reached")
                return Response({
                    "error": "Meter data not found"
                }, status=status.HTTP_404_NOT_FOUND)
            print(f"Serializing data with id={data.id}")
            serializer = MeterDataSerializer(data)
            return Response({
                "details": {
                    "message": "Meter data retrieved successfully",
                    "data": serializer.data
                }
            }, status=status.HTTP_200_OK)
        except MeterData.DoesNotExist:
            print(f"MeterData with meter={pk} does not exist")
            return Response({
                "error": "Meter data not found"
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(f"Exception occurred: {str(e)}")
            return Response({
                "error": "Error retrieving meter data",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def create(self, request):
        """Create a new meter data point from API payload"""
        try:
            # Extract meter_id from payload
            meter_id = request.data.get('meter_id')
            data = request.data.get('data', {})

            if not meter_id:
                return Response({
                    "error": "meter_id is required"
                }, status=status.HTTP_400_BAD_REQUEST)

            # Get the meter
            try:
                meter = Meter.objects.get(device_id=meter_id)
            except Meter.DoesNotExist:
                return Response({
                    "error": f"Meter with device_id {meter_id} not found"
                }, status=status.HTTP_404_NOT_FOUND)

            # Prepare data object
            meter_data = {
                'meter': meter.id,
                'engine_hours': data.get('engine_hours', 0),
                'frequency_hz': data.get('frequency_hz', 0),
                'power_percentage': data.get('power_percentage', 0),

                # Phase data
                'phase_a_voltage_v': data.get('phase_a', {}).get('voltage_v', 0),
                'phase_a_current_a': data.get('phase_a', {}).get('current_a', 0),
                'phase_b_voltage_v': data.get('phase_b', {}).get('voltage_v', 0),
                'phase_b_current_a': data.get('phase_b', {}).get('current_a', 0),
                'phase_c_voltage_v': data.get('phase_c', {}).get('voltage_v', 0),
                'phase_c_current_a': data.get('phase_c', {}).get('current_a', 0),

                # Other measurements
                'coolant_temp_c': data.get('coolant_temp_c', 0),
                'oil_pressure_kpa': data.get('oil_pressure_kpa', 0),
                'battery_voltage_v': data.get('battery_voltage_v', 0),
                'fuel_level_percent': data.get('fuel_level_percent', 0),
                'rpm': data.get('rpm', 0),
                'oil_temp_c': data.get('oil_temp_c', 0),
                'boost_pressure_kpa': data.get('boost_pressure_kpa', 0),
                'intake_air_temp_c': data.get('intake_air_temp_c', 0),
                'fuel_rate_lph': data.get('fuel_rate_lph', 0),
                'instantaneous_power_kw': data.get('instantaneous_power_kw', 0),

                # Alarms
                'alarm_emergency_stop': data.get('alarms', {}).get('emergency_stop', False),
                'alarm_low_oil_pressure': data.get('alarms', {}).get('low_oil_pressure', False),
                'alarm_high_coolant_temp': data.get('alarms', {}).get('high_coolant_temp', False),
                'alarm_low_coolant_level': data.get('alarms', {}).get('low_coolant_level', False),
                'alarm_crank_failure': data.get('alarms', {}).get('crank_failure', False),
            }

            # Validate and save
            serializer = MeterDataSerializer(data=meter_data)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "details": {
                        "message": "Meter data recorded successfully",
                        "data": serializer.data
                    }
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    "error": "Invalid data",
                    "details": serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({
                "error": "Error recording meter data",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'])
    def latest(self, request):
        """Get latest data for each meter"""
        try:
            latest_data = {}
            for meter in Meter.objects.all():
                data = MeterData.objects.filter(meter=meter).order_by('-timestamp').first()
                if data:
                    latest_data[meter.device_id] = MeterDataSerializer(data).data

            return Response({
                "details": {
                    "message": "Latest meter data retrieved successfully",
                    "data": latest_data
                }
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "error": "Error retrieving latest meter data",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class GenerateAlarmReport(viewsets.ViewSet):
    def create(self, request):
        """
        Generate an alarm report for a specific meter and return a download URL.
        """
        try:
            meter_id = request.data.get('meter_id')
            time_range = request.data.get('time_range', 'last_24h')  # Options: last_24h, last_7d, etc.

            if not meter_id:
                return Response({
                    "error": "meter_id is required"
                }, status=status.HTTP_400_BAD_REQUEST)

            # Get the meter
            try:
                meter = Meter.objects.get(device_id=meter_id)
            except Meter.DoesNotExist:
                return Response({
                    "error": f"Meter with device_id {meter_id} not found"
                }, status=status.HTTP_404_NOT_FOUND)

            # Query data based on time range
            query = MeterData.objects.filter(meter=meter).order_by('-timestamp')

            if time_range == 'last_24h':
                start_time = timezone.now() - timezone.timedelta(hours=24)
                query = query.filter(timestamp__gte=start_time)
            elif time_range == 'last_7d':
                start_time = timezone.now() - timezone.timedelta(days=7)
                query = query.filter(timestamp__gte=start_time)

            data_points = list(query)

            if not data_points:
                return Response({
                    "error": "No data found for this meter in the specified time range"
                }, status=status.HTTP_404_NOT_FOUND)

            # Create Excel file
            excel_data = {
                'timestamp': [],
                'emergency_stop': [],
                'low_oil_pressure': [],
                'high_coolant_temp': [],
                'low_coolant_level': [],
                'crank_failure': [],
                'coolant_temp_c': [],
                'oil_pressure_kpa': [],
                'engine_hours': [],
                'fuel_level_percent': []
            }

            for data in data_points:
                # Convert timezone-aware datetime to timezone-naive datetime
                naive_timestamp = data.timestamp.replace(tzinfo=None)
                excel_data['timestamp'].append(naive_timestamp)
                excel_data['emergency_stop'].append('Yes' if data.alarm_emergency_stop else 'No')
                excel_data['low_oil_pressure'].append('Yes' if data.alarm_low_oil_pressure else 'No')
                excel_data['high_coolant_temp'].append('Yes' if data.alarm_high_coolant_temp else 'No')
                excel_data['low_coolant_level'].append('Yes' if data.alarm_low_coolant_level else 'No')
                excel_data['crank_failure'].append('Yes' if data.alarm_crank_failure else 'No')
                excel_data['coolant_temp_c'].append(data.coolant_temp_c)
                excel_data['oil_pressure_kpa'].append(data.oil_pressure_kpa)
                excel_data['engine_hours'].append(data.engine_hours)
                excel_data['fuel_level_percent'].append(data.fuel_level_percent)

            # Create DataFrame and excel file
            df = pd.DataFrame(excel_data)

            # Create a buffer to save the Excel file
            buffer = BytesIO()

            # Create Excel writer
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                df.to_excel(writer, sheet_name='Alarm Report', index=False)
                workbook = writer.book
                worksheet = writer.sheets['Alarm Report']

                # Add some formatting
                header_format = workbook.add_format({
                    'bold': True,
                    'text_wrap': True,
                    'valign': 'top',
                    'bg_color': '#D7E4BC',
                    'border': 1
                })

                # Write the header with the header format
                for col_num, value in enumerate(df.columns.values):
                    worksheet.write(0, col_num, value, header_format)
                    # Set column width based on content
                    worksheet.set_column(col_num, col_num, 18)

            # Save the Excel file
            timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
            filename = f"alarm_report_{meter_id}_{timestamp}.xlsx"
            file_path = f"reports/{filename}"

            # Reset buffer position
            buffer.seek(0)

            # Save to storage
            default_storage.save(file_path, ContentFile(buffer.getvalue()))

            # Generate download URL
            # Note: You'll need to set up a URL pattern to serve these files
            download_url = request.build_absolute_uri(f'/media/{file_path}')

            return Response({
                "details": {
                    "message": "Alarm report generated successfully",
                    "filename": filename,
                    "download_url": download_url
                }
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "error": "Error generating alarm report",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def retrieve(self, request, pk=None):
        """
        Download a specific report by filename
        """
        try:
            filename = pk
            file_path = f"reports/{filename}"

            if not default_storage.exists(file_path):
                return Response({
                    "error": "Report file not found"
                }, status=status.HTTP_404_NOT_FOUND)

            # Read the file
            file_content = default_storage.open(file_path).read()

            # Create HTTP response with file
            response = HttpResponse(
                file_content,
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = f'attachment; filename="{filename}"'

            return response

        except Exception as e:
            return Response({
                "error": "Error downloading report",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class GenerateMeterReport(viewsets.ViewSet):
    def create(self, request):
        """
        Generate a comprehensive report with all meter data for a specific meter.
        """
        try:
            meter_id = request.data.get('meter_id')
            time_range = request.data.get('time_range', 'last_24h')  # Options: last_24h, last_7d, etc.

            if not meter_id:
                return Response({
                    "error": "meter_id is required"
                }, status=status.HTTP_400_BAD_REQUEST)

            # Get the meter
            try:
                meter = Meter.objects.get(device_id=meter_id)
            except Meter.DoesNotExist:
                return Response({
                    "error": f"Meter with device_id {meter_id} not found"
                }, status=status.HTTP_404_NOT_FOUND)

            # Query data based on time range
            query = MeterData.objects.filter(meter=meter).order_by('-timestamp')

            if time_range == 'last_24h':
                start_time = timezone.now() - timezone.timedelta(hours=24)
                query = query.filter(timestamp__gte=start_time)
            elif time_range == 'last_7d':
                start_time = timezone.now() - timezone.timedelta(days=7)
                query = query.filter(timestamp__gte=start_time)
            elif time_range == 'last_30d':
                start_time = timezone.now() - timezone.timedelta(days=30)
                query = query.filter(timestamp__gte=start_time)
            elif time_range == 'all':
                # All data, no filtering
                pass

            data_points = list(query)

            if not data_points:
                return Response({
                    "error": "No data found for this meter in the specified time range"
                }, status=status.HTTP_404_NOT_FOUND)

            # Create Excel file with all meter data fields
            excel_data = {
                'timestamp': [],
                # Power metrics
                'frequency_hz': [],
                'power_percentage': [],
                'instantaneous_power_kw': [],
                # Engine metrics
                'engine_hours': [],
                'rpm': [],
                # Phase data
                'phase_a_voltage_v': [],
                'phase_a_current_a': [],
                'phase_b_voltage_v': [],
                'phase_b_current_a': [],
                'phase_c_voltage_v': [],
                'phase_c_current_a': [],
                # Temperature and pressure
                'coolant_temp_c': [],
                'oil_temp_c': [],
                'intake_air_temp_c': [],
                'oil_pressure_kpa': [],
                'boost_pressure_kpa': [],
                # Fuel metrics
                'fuel_level_percent': [],
                'fuel_rate_lph': [],
                # Battery
                'battery_voltage_v': [],
                # Alarms
                'alarm_emergency_stop': [],
                'alarm_low_oil_pressure': [],
                'alarm_high_coolant_temp': [],
                'alarm_low_coolant_level': [],
                'alarm_crank_failure': [],
            }

            for data in data_points:
                # Convert timezone-aware datetime to timezone-naive datetime
                naive_timestamp = data.timestamp.replace(tzinfo=None)
                excel_data['timestamp'].append(naive_timestamp)

                # Power metrics
                excel_data['frequency_hz'].append(data.frequency_hz)
                excel_data['power_percentage'].append(data.power_percentage)
                excel_data['instantaneous_power_kw'].append(data.instantaneous_power_kw)

                # Engine metrics
                excel_data['engine_hours'].append(data.engine_hours)
                excel_data['rpm'].append(data.rpm)

                # Phase data
                excel_data['phase_a_voltage_v'].append(data.phase_a_voltage_v)
                excel_data['phase_a_current_a'].append(data.phase_a_current_a)
                excel_data['phase_b_voltage_v'].append(data.phase_b_voltage_v)
                excel_data['phase_b_current_a'].append(data.phase_b_current_a)
                excel_data['phase_c_voltage_v'].append(data.phase_c_voltage_v)
                excel_data['phase_c_current_a'].append(data.phase_c_current_a)

                # Temperature and pressure
                excel_data['coolant_temp_c'].append(data.coolant_temp_c)
                excel_data['oil_temp_c'].append(data.oil_temp_c)
                excel_data['intake_air_temp_c'].append(data.intake_air_temp_c)
                excel_data['oil_pressure_kpa'].append(data.oil_pressure_kpa)
                excel_data['boost_pressure_kpa'].append(data.boost_pressure_kpa)

                # Fuel metrics
                excel_data['fuel_level_percent'].append(data.fuel_level_percent)
                excel_data['fuel_rate_lph'].append(data.fuel_rate_lph)

                # Battery
                excel_data['battery_voltage_v'].append(data.battery_voltage_v)

                # Alarms
                excel_data['alarm_emergency_stop'].append('Yes' if data.alarm_emergency_stop else 'No')
                excel_data['alarm_low_oil_pressure'].append('Yes' if data.alarm_low_oil_pressure else 'No')
                excel_data['alarm_high_coolant_temp'].append('Yes' if data.alarm_high_coolant_temp else 'No')
                excel_data['alarm_low_coolant_level'].append('Yes' if data.alarm_low_coolant_level else 'No')
                excel_data['alarm_crank_failure'].append('Yes' if data.alarm_crank_failure else 'No')

            # Create DataFrame and excel file
            df = pd.DataFrame(excel_data)

            # Create a buffer to save the Excel file
            buffer = BytesIO()

            # Create Excel writer
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                df.to_excel(writer, sheet_name='Meter Data Report', index=False)
                workbook = writer.book
                worksheet = writer.sheets['Meter Data Report']

                # Add some formatting
                header_format = workbook.add_format({
                    'bold': True,
                    'text_wrap': True,
                    'valign': 'top',
                    'bg_color': '#D7E4BC',
                    'border': 1
                })

                # Format for numeric columns
                number_format = workbook.add_format({'num_format': '#,##0.00'})

                # Write the header with the header format
                for col_num, value in enumerate(df.columns.values):
                    worksheet.write(0, col_num, value, header_format)
                    # Set column width based on content
                    worksheet.set_column(col_num, col_num, 18)

                # Apply number formatting to numeric columns
                for col_num, column in enumerate(df.columns):
                    if column not in ['timestamp', 'alarm_emergency_stop', 'alarm_low_oil_pressure',
                                     'alarm_high_coolant_temp', 'alarm_low_coolant_level', 'alarm_crank_failure']:
                        worksheet.set_column(col_num, col_num, 18, number_format)

            # Save the Excel file
            timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
            filename = f"meter_data_report_{meter_id}_{timestamp}.xlsx"
            file_path = f"reports/{filename}"

            # Reset buffer position
            buffer.seek(0)

            # Save to storage
            default_storage.save(file_path, ContentFile(buffer.getvalue()))

            # Generate download URL
            download_url = request.build_absolute_uri(f'/media/{file_path}')

            return Response({
                "details": {
                    "message": "Complete meter data report generated successfully",
                    "filename": filename,
                    "download_url": download_url
                }
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "error": "Error generating meter data report",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
