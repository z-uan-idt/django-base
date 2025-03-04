import os
import shutil
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path


# Templates
class Templates:
    @staticmethod
    def apps_template(name, verbose_name, app_path):
        return f"""from django.apps import AppConfig


class {name}Config(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    verbose_name = '{verbose_name}'
    name = '{app_path}'
"""

    @staticmethod
    def admin_template():
        return """from django.contrib import admin

# Register your models here.
"""

    @staticmethod
    def urls_template(name):
        name_cap = str(name).capitalize()
        return f"""from rest_framework.routers import DefaultRouter
from django.urls import path, include

from .views.{name}_view import {name_cap}ViewAPI


api_router = DefaultRouter(trailing_slash=False)
api_router.register(prefix="{name}", viewset={name_cap}ViewAPI, basename="{name}")

{name}_urlpatterns = [
    path("api/v1/", include(api_router.urls)),
]
"""

    @staticmethod
    def view_template(name):
        name_cap = str(name).capitalize()
        return f"""from rest_framework.permissions import IsAuthenticated
from utils.views import APIGenericView
from django.db import transaction

from utils.decorators import api

from ..serializers import request_serializer, response_serializer
from ..services.{name}_service import {name_cap}Service
from ..docs import {name}_swagger


class {name_cap}ViewAPI(APIGenericView):
    permission_classes = [IsAuthenticated]
    
    {name}_service = {name_cap}Service()

    action_serializers = {{
        "list_request": request_serializer.List{name_cap}Serializer,
        "list_response": response_serializer.{name_cap}Serializer,
        "create_request": request_serializer.{name_cap}Serializer,
        "create_response": response_serializer.{name_cap}Serializer,
        "update_request": request_serializer.{name_cap}Serializer,
        "update_response": response_serializer.{name_cap}Serializer,
        "retrieve_response": response_serializer.{name_cap}Serializer,
    }}

    @api.swagger(
        tags=["{name_cap}"],
        operation_id='{name_cap} List',
        manual_parameters=[
            {name}_swagger.PAGE_PARAMETER,
            {name}_swagger.LIMIT_PARAMETER,
            {name}_swagger.KEYWORD_PARAMETER,
            {name}_swagger.ORDER_BY_PARAMETER,
        ]
    )
    def list(self, request):
        serializer = self.get_request_serializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        {name}s = self.{name}_service.get_{name}s(**serializer.validated_data)
        return self.paginator({name}s, many=True)

    @api.swagger(
        tags=["{name_cap}"],
        operation_id='{name_cap} Create'
    )
    @transaction.atomic
    def create(self, request):
        serializer = self.get_request_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        return self.get_response_serializer(instance).data

    @api.swagger(
        tags=["{name_cap}"],
        operation_id='{name_cap} Detail'
    )
    def retrieve(self, request, pk):
        instance = self.{name}_service.get_{name}_by_id(pk)
        return self.get_response_serializer(instance).data

    @api.swagger(
        tags=["{name_cap}"],
        operation_id='{name_cap} Delete'
    )
    @transaction.atomic
    def destroy(self, request, pk):
        self.{name}_service.delete_{name}_by_id(pk)

    @api.swagger(
        tags=["{name_cap}"],
        operation_id='{name_cap} Update'
    )
    @transaction.atomic
    def update(self, request, pk):
        instance = self.{name}_service.get_{name}_by_id(pk)
        serializer = self.get_request_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        {name} = serializer.save()
        return self.get_response_serializer({name}).data
"""

    @staticmethod
    def docs_template():
        return """from drf_yasg import openapi

from utils.paginator import Paginator


PAGE_PARAMETER = openapi.Parameter(
    name="page",
    required=False,
    in_=openapi.IN_QUERY,
    type=openapi.TYPE_INTEGER,
    description="Page",
    default=Paginator.DEFAULT_PAGE
)

LIMIT_PARAMETER = openapi.Parameter(
    name="limit",
    required=False,
    in_=openapi.IN_QUERY,
    type=openapi.TYPE_INTEGER,
    description="Page limit",
    default=Paginator.DEFAULT_PER_PAGE
)

KEYWORD_PARAMETER = openapi.Parameter(
    name="keyword",
    required=False,
    in_=openapi.IN_QUERY,
    type=openapi.TYPE_STRING,
    description="Keyword search",
)

ORDER_BY_PARAMETER = openapi.Parameter(
    name="order_by",
    required=False,
    in_=openapi.IN_QUERY,
    type=openapi.TYPE_STRING,
    description="order_by: [asc, desc]",
)"""

    @staticmethod
    def services_template(name, init_model):
        name_cap = str(name).capitalize()
        return f"""from utils.decorators import singleton
from django.db import models

from ..models import {init_model}


@singleton
class {name_cap}Service:
    {name}_objects = {init_model}.objects
    
    def get_{name}s(self, keyword=None, **kwargs):
        filter_query = models.Q()

        if keyword and keyword.strip():
            keyword = keyword.strip()

        {name}s = self.{name}_objects.filter(filter_query)

        order_by = str(kwargs.get("order_by") or "asc").lower()

        if order_by == "asc":
            {name}s = {name}s.order_by("created_at")
        else:
            {name}s = {name}s.order_by("-created_at")

        return {name}s
        
    def get_{name}_by_id(self, id: int):
        return self.{name}_objects.get(pk=id)
        
    def delete_{name}_by_id(self, id: int):
        instance = self.{name}_objects.get(pk=id)
        instance.delete()
        
    def create_{name}(self, **kwargs):
        instance = self.{name}_objects.create(**kwargs)
        return instance

    def update_{name}(self, instance, **kwargs):
        for key, value in kwargs.items():
            setattr(instance, key, value)
        
        instance.save()
        
        return instance
"""

    @staticmethod
    def request_serializer_template(name, init_model):
        name_cap = str(name).capitalize()
        return f"""from rest_framework import serializers
from utils.paginator import Paginator

from ..models import {init_model}
from ..services.{name}_service import {name_cap}Service


class List{name_cap}Serializer(serializers.Serializer):
    page = serializers.IntegerField(
        default=Paginator.DEFAULT_PAGE,
        required=False,
    )
    limit = serializers.IntegerField(
        default=Paginator.DEFAULT_PER_PAGE,
        required=False,
    )
    keyword = serializers.CharField(
        allow_blank=True,
        required=False,
        default="",
    )
    order_by = serializers.CharField(
        allow_blank=True,
        required=False,
        default="",
    )
       
 
class {name_cap}Serializer(serializers.ModelSerializer):

    class Meta:
        model = {init_model}
        service = {name_cap}Service()
        fields = '__all__'
    
    def create(self, validated_data):
        return self.Meta.service.create_{name}(**validated_data)
    
    def update(self, instance, validated_data):
        return self.Meta.service.update_{name}(instance, **validated_data)"""

    @staticmethod
    def response_serializer_template(name, init_model):
        name_cap = str(name).capitalize()
        return f"""from rest_framework import serializers

from apps.{name}.models import {init_model}


class {name_cap}Serializer(serializers.ModelSerializer):

    class Meta:
        model = {init_model}
        fields = '__all__'"""


class AppGenerator:
    def __init__(self, app_name, init_model, verbose_name=None, base_dir=None):
        self.base_dir = Path(base_dir) if base_dir else Path.cwd()
        self.app_name = str(app_name).lower()
        self.init_model = str(init_model).capitalize()
        self.verbose_name = str(verbose_name or app_name).capitalize()
        self.app_dir = self.base_dir / "apps" / self.app_name
        
        self.folder_includes = ["docs", "migrations", "models", "serializers", "services", "views"]
        self.file_includes = ["__init__.py", "admin.py", "apps.py", "urls.py"]
        
    def clean_app(self):
        """Remove files and folders not in the includes lists"""
        if not self.app_dir.exists():
            return

        for item in os.listdir(self.app_dir):
            item_path = self.app_dir / item
            
            if item_path.is_dir() and item not in self.folder_includes and not item.startswith('.'):
                shutil.rmtree(item_path)
            elif item_path.is_file() and item not in self.file_includes and not item.startswith('.'):
                os.remove(item_path)
    
    def create_file(self, path, content):
        """Create a file with the given content if it doesn't exist"""
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False
    
    def create_app_structure(self):
        """Create the app structure with files and folders"""
        # Create app directory if it doesn't exist
        self.app_dir.mkdir(parents=True, exist_ok=True)
        
        # Create each included folder
        for folder in self.folder_includes:
            folder_path = self.app_dir / folder
            folder_path.mkdir(exist_ok=True)
            
            # Create __init__.py in each folder
            self.create_file(folder_path / "__init__.py", "")
            
            # Create specific files in each folder
            if folder == "serializers":
                self.create_file(
                    folder_path / "request_serializer.py", 
                    Templates.request_serializer_template(self.app_name, self.init_model)
                )
                self.create_file(
                    folder_path / "response_serializer.py", 
                    Templates.response_serializer_template(self.app_name, self.init_model)
                )
            elif folder == "views":
                self.create_file(
                    folder_path / f"{self.app_name}_view.py", 
                    Templates.view_template(self.app_name)
                )
            elif folder == "services":
                self.create_file(
                    folder_path / f"{self.app_name}_service.py", 
                    Templates.services_template(self.app_name, self.init_model)
                )
            elif folder == "docs":
                self.create_file(
                    folder_path / f"{self.app_name}_swagger.py", 
                    Templates.docs_template()
                )
        
        # Create root files
        for file in self.file_includes:
            file_path = self.app_dir / file
            
            if file == "apps.py":
                self.create_file(
                    file_path, 
                    Templates.apps_template(
                        str(self.app_name).capitalize(), 
                        self.verbose_name, 
                        f"apps.{self.app_name}"
                    )
                )
            elif file == "admin.py":
                self.create_file(file_path, Templates.admin_template())
            elif file == "urls.py":
                self.create_file(file_path, Templates.urls_template(self.app_name))
            else:
                self.create_file(file_path, "")
    
    def generate(self):
        """Generate the app structure"""
        try:
            self.clean_app()
            self.create_app_structure()
            return True, f"App '{self.app_name}' generated successfully!"
        except Exception as e:
            return False, f"Error generating app: {str(e)}"


class DjangoAppGeneratorUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Django App Generator")
        self.root.geometry("600x500")
        self.root.resizable(True, True)
        
        # Set project directory (defaults to current directory)
        self.project_dir = Path.cwd()
        
        self.create_widgets()
        self.populate_app_list()
    
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Tab control
        self.tab_control = ttk.Notebook(main_frame)
        
        # Create App Tab
        create_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(create_tab, text="Create")
        
        # Manage Apps Tab
        manage_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(manage_tab, text="Manage")
        
        self.tab_control.pack(fill=tk.BOTH, expand=True)
        
        # Create App Tab Content
        self.setup_create_tab(create_tab)
        
        # Manage Apps Tab Content
        self.setup_manage_tab(manage_tab)
        
        # Status bar
        status_frame = ttk.Frame(self.root, relief=tk.SUNKEN)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_label = ttk.Label(status_frame, textvariable=self.status_var, anchor=tk.W)
        status_label.pack(fill=tk.X, padx=5, pady=2)
    
    def setup_create_tab(self, parent):
        # Project directory frame
        dir_frame = ttk.LabelFrame(parent, text="Project Directory", padding="10")
        dir_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.dir_var = tk.StringVar(value=str(self.project_dir))
        dir_entry = ttk.Entry(dir_frame, textvariable=self.dir_var, width=50)
        dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        browse_btn = ttk.Button(dir_frame, text="Browse", command=self.browse_directory)
        browse_btn.pack(side=tk.RIGHT)
        
        # App details frame
        details_frame = ttk.LabelFrame(parent, text="App Details", padding="10")
        details_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # App name
        ttk.Label(details_frame, text="App Name*:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.app_name_var = tk.StringVar()
        ttk.Entry(details_frame, textvariable=self.app_name_var, width=30).grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Vietnamese name
        ttk.Label(details_frame, text="Vietnamese Name:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.vi_name_var = tk.StringVar()
        ttk.Entry(details_frame, textvariable=self.vi_name_var, width=30).grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Initial model
        ttk.Label(details_frame, text="Initial Model*:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.init_model_var = tk.StringVar()
        ttk.Entry(details_frame, textvariable=self.init_model_var, width=30).grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Folders to include
        ttk.Label(details_frame, text="Included Folders:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.folders_text = tk.Text(details_frame, height=3, width=30)
        self.folders_text.grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)
        self.folders_text.insert(tk.END, "docs, migrations, models, serializers, services, views")
        
        # Files to include
        ttk.Label(details_frame, text="Included Files:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
        self.files_text = tk.Text(details_frame, height=3, width=30)
        self.files_text.grid(row=4, column=1, sticky=tk.W, padx=5, pady=5)
        self.files_text.insert(tk.END, "__init__.py, admin.py, apps.py, urls.py")
        
        # Action buttons
        buttons_frame = ttk.Frame(parent)
        buttons_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(buttons_frame, text="Clear", command=self.clear_form).pack(side=tk.RIGHT, padx=5)
        ttk.Button(buttons_frame, text="Generate", command=self.generate_app).pack(side=tk.RIGHT)
    
    def setup_manage_tab(self, parent):
        # App list frame
        list_frame = ttk.LabelFrame(parent, text="Existing Apps", padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create treeview
        columns = ("name", "path")
        self.app_tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        
        # Define headings
        self.app_tree.heading("name", text="apps")
        self.app_tree.heading("path", text="path")
        
        # Define columns
        self.app_tree.column("name", width=100)
        self.app_tree.column("path", width=350)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.app_tree.yview)
        self.app_tree.configure(yscroll=scrollbar.set)
        
        # Pack the treeview and scrollbar
        self.app_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Action buttons for managing apps
        buttons_frame = ttk.Frame(parent)
        buttons_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(buttons_frame, text="Refresh", command=self.populate_app_list).pack(side=tk.LEFT)
        ttk.Button(buttons_frame, text="Delete", command=self.delete_app).pack(side=tk.LEFT)
    
    def browse_directory(self):
        dir_path = filedialog.askdirectory(initialdir=self.project_dir)
        if dir_path:
            self.project_dir = Path(dir_path)
            self.dir_var.set(str(self.project_dir))
            self.populate_app_list()
    
    def clear_form(self):
        self.app_name_var.set("")
        self.vi_name_var.set("")
        self.init_model_var.set("")
        
        # Reset folders and files to default
        self.folders_text.delete(1.0, tk.END)
        self.folders_text.insert(tk.END, "docs, migrations, models, serializers, services, views")
        
        self.files_text.delete(1.0, tk.END)
        self.files_text.insert(tk.END, "__init__.py, admin.py, apps.py, urls.py")
        
        self.status_var.set("")
    
    def generate_app(self):
        app_name = self.app_name_var.get().strip()
        init_model = self.init_model_var.get().strip()
        
        if not app_name:
            messagebox.showerror("Error", "App name is required!")
            return
        
        if not init_model:
            messagebox.showerror("Error", "Initial model is required!")
            return
        
        # Get folder and file includes
        folders_str = self.folders_text.get(1.0, tk.END).strip()
        files_str = self.files_text.get(1.0, tk.END).strip()
        
        folder_includes = [f.strip() for f in folders_str.split(',')]
        file_includes = [f.strip() for f in files_str.split(',')]
        
        # Create app generator
        generator = AppGenerator(
            app_name=app_name,
            init_model=init_model,
            verbose_name=self.vi_name_var.get().strip() or None,
            base_dir=self.project_dir
        )
        
        # Update folder and file includes
        generator.folder_includes = folder_includes
        generator.file_includes = file_includes
        
        # Generate app
        success, message = generator.generate()
        
        if success:
            messagebox.showinfo("Success", message)
            self.status_var.set(message)
            self.populate_app_list()
            self.clear_form()
        else:
            messagebox.showerror("Error", message)
            self.status_var.set(message)
    
    def populate_app_list(self):
        # Clear existing items
        for item in self.app_tree.get_children():
            self.app_tree.delete(item)
        
        # Check if apps directory exists
        apps_dir = self.project_dir / "apps"
        if not apps_dir.exists() or not apps_dir.is_dir():
            self.status_var.set("Apps directory not found")
            return
        
        # Find all Django apps
        for app_dir in apps_dir.iterdir():
            if app_dir.is_dir() and (app_dir / "apps.py").exists():
                app_name = app_dir.name
                
                # Try to find main model
                models_dir = app_dir / "models"
                main_model = "Unknown"
                
                if models_dir.exists() and models_dir.is_dir():
                    model_files = list(models_dir.glob("*.py"))
                    if model_files:
                        main_model = model_files[0].stem.capitalize()
                
                self.app_tree.insert("", "end", values=(app_name, str(app_dir), main_model))
        
        self.status_var.set(f"Found {len(self.app_tree.get_children())} apps")
    
    def delete_app(self):
        selected = self.app_tree.selection()
        if not selected:
            messagebox.showinfo("Info", "Please select an app to delete")
            return
        
        app_data = self.app_tree.item(selected[0], "values")
        app_name = app_data[0]
        app_path = app_data[1]
        
        # Confirm deletion
        if messagebox.askyesno("Confirm", f"Are you sure you want to delete the app '{app_name}'?\nThis action cannot be undone."):
            try:
                shutil.rmtree(app_path)
                self.populate_app_list()
                self.status_var.set(f"App '{app_name}' deleted successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete app: {str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = DjangoAppGeneratorUI(root)
    root.mainloop()